import liiondb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

[dfndb, db_connection] = liiondb.fn_db.liiondb()

# Utitlity functions


def getTableColumnName(tablename):
    """get all column in the given table"""
    QUERY = "SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{0}'".format(tablename)
    df = pd.read_sql(QUERY, dfndb)
    return df


def fetchData(df, material, parameter):
    """select a row based on material and parameter string
    (can be a substring)"""
    ind = (df['material'].str.contains(material)
           & df['parameter'].str.contains(parameter))
    return df[ind]


def printData(df, material, parameter):
    """get a function literal string using given material and parameter,
    decode it and return the string"""
    d = fetchData(df, material, parameter)
    str = "\n\n# Material:  {0}, Parameter: {1}, Unit: {2}\n\n".format(
        d['material'].iloc[0],
        d['parameter'].iloc[0],
        d['units_output'].iloc[0]
    )
    str = str + d['function'].iloc[0].tobytes().decode()
    return str


def convertArray(raw_data):
    """convert json formatted array to numpy"""
    csv_array = raw_data
    csv_array = csv_array.replace("{", "[")
    csv_array = csv_array.replace("}", "]")
    csv_list = eval(csv_array)
    raw_data = csv_list
    data = np.array(raw_data)
    return data


def writeTabulatedFunctionToFile(fnsetup, df, parameter, material):
    """For function given with tabulated array,
    for the given parameter and material,
    write out the matlab interpolation table.
    The input argument fnsetup contains filename and function signature,
    see example below"""
    sdf = fetchData(df, parameter, material)
    data = sdf['raw_data'].iloc[0]
    data = convertArray(data)

    def getval(fd):
        return sdf[fd].iloc[0]

    with open("{0}.m".format(fnsetup['filename']), 'w') as f:
        f.write(fnsetup['signature'] + "\n\n")
        f.write("% Material : {0}, parameter : {1}, unit : {2}\n\n".format(getval('material'), getval('parameter'), getval('units_output')))
        f.write("% Reference :\n")
        f.write("% Authors : {0}\n% Title : {1}\n% doi : {2}\n\n".format(getval('authors'), getval('title'), getval('doi')))
        f.write("data = [")
        for i in range(data.shape[0]):
            f.write('{:g}, {:g};\n'.format(data[i, 0], data[i, 1]))
        f.write("];\n")
        f.write("{0} = interpTable(data(:, 1), data(:, 2), {1});\n".format(fnsetup['out'], fnsetup['in']))
        f.write("end\n")


QUERY = '''SELECT DISTINCT data.data_id as dataid,
parameter.name as parameter,
material.name as material,
data.raw_data,
data.raw_data_class,
data.function,
parameter.units_output,
paper.authors,
paper.title,
paper.doi,
paper.paper_id
FROM data
JOIN paper ON paper.paper_id = data.paper_id
JOIN material ON material.material_id = data.material_id
JOIN parameter ON parameter.parameter_id = data.parameter_id
'''


# Sturm paper
df = pd.read_sql(QUERY, dfndb)
df = df[df['paper_id'] == 51]

fnsetup = dict()
fnsetup['filename'] = "computeOCPFunc_Graphite_paper"
fnsetup['signature'] = "function [OCP, dUdT] = {0}(c, T, cmax)".\
    format(fnsetup['filename'])
fnsetup['in'] = "stoc"
fnsetup['out'] = "OCP"

writeTabulatedFunctionToFile(fnsetup, df, 'Graphite', 'half cell')


# Chen paper
df = pd.read_sql(QUERY, dfndb)
df = df[df['paper_id'] == 5]
df = df.sort_values('material')

filename = 'liiondb_output2.py'
with open(filename, 'w') as f:
    f.write(printData('LiPF6', 'ionic conductivity'))
    f.write(printData('LiPF6', 'diffusion coefficient'))
