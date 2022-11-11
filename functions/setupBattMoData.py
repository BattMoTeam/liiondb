import fn_db
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

[dfndb, db_connection] = fn_db.liiondb()

QUERY = '''
        SELECT DISTINCT data.data_id as dataid, parameter.name as parameter, material.name as material, data.raw_data, data.raw_data_class, data.function, parameter.units_output, paper.paper_tag, paper.doi
        FROM data
        JOIN paper ON paper.paper_id = data.paper_id
        JOIN material ON material.material_id = data.material_id
        JOIN parameter ON parameter.parameter_id = data.parameter_id
        WHERE material.name = 'Silicon'
        '''

df = pd.read_sql(QUERY, dfndb)


def convertArray(raw_data):
    csv_array = raw_data
    csv_array = csv_array.replace("{", "[")
    csv_array = csv_array.replace("}", "]")
    csv_list = eval(csv_array)
    raw_data = csv_list
    raw_data = np.array(raw_data)
    return raw_data


ocp = df['raw_data'][df['dataid'] == 818]
ocp = ocp.iloc[0]
ocp = convertArray(ocp)

plt.plot(ocp[:, 0], ocp[:, 1])
plt.show()

with open('computeOCPSiliconLi2012.m', 'w') as f:
    f.write('stoc_vals = [')
    for x in ocp[:, 0]:
        f.write('{:g}\n'.format(x))
    f.write('];')
    f.write('OCP_vals = [')
    for x in ocp[:, 1]:
        f.write('{:g}\n'.format(x))
    f.write('];')    
