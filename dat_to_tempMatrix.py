from struct import unpack
import numpy as np
import pandas as pd


XLSX_FILE_PATH = "537.xlsx"
BINARY_FILE_PATH = "TH922537.SIX"

DATA_LENGTH = 0x96000
MATRIX_HEIGTH = 480
MATRIX_WIDTH = 640

def xlsx_to_ndarray(filePath):

    df = pd.read_excel(filePath)
    xlsxRawArray = df.drop([328,329,650,651,972,973,]).iloc[8:,1:].T.to_numpy()
    xlsArray = np.concatenate([ \
        xlsxRawArray[:,:xlsxRawArray.shape[1]//2],\
        xlsxRawArray[:,xlsxRawArray.shape[1]//2:]\
        ]).astype(np.float32)

    return xlsArray

def dat_six_to_ndarray(filePath):
    '''
    サーモグラフィの生データSIXから温度のマトリックスを出力する
    '''

    with open(filePath, 'rb') as f:
        header = f.read(0x400)
        a0 = unpack('>e', b'\x01\x00')[0]
        a1 = unpack(">H", header[0x36:0x38])[0]
        T0 = unpack(">H", header[0x30:0x32])[0]

        data = np.fromfile(f, dtype=">h",count=DATA_LENGTH//2 )
        dataArray = data.reshape(MATRIX_HEIGTH, MATRIX_WIDTH).astype(np.float16)
        tempArray = a0*a1*dataArray + T0

    return tempArray
    #return data

def Effect_of_variables(x,y,d_hex):
    xls = xlsx_to_ndarray(XLSX_FILE_PATH)
    data = dat_six_to_ndarray(BINARY_FILE_PATH)

    print(f'変数のバイナリ値:::{d_hex}')
    print(f'({x},{y})座標の温度:::{xls[y,x]}度')
    print(f'({x},{y})座標のバイナリ値:::{data[y,x]}')

    xlsFlat = xls.flatten()
    dataFlat = data.flatten()

    coef_1 = np.polyfit(dataFlat,xlsFlat,1)

    print(f'係数a:::{coef_1[0]}')
    print(f'係数b:::{coef_1[1]}')
    

def compare(T1,T2,d_hex1,d_hex2,x1,y1,x2,y2):
    data = dat_six_to_ndarray(BINARY_FILE_PATH)

    D1 = data[y1,x1]
    D2 = data[y2,x2]

    a = (T1-T2)/(D1-D2)
    T0 = (-1*D2*T2+D1*T2)/(D1-D2)

    print("==========================")
    print(f'変数のバイナリ値:::{d_hex1}, {d_hex2}')
    print(f'係数a:::{a}')
    print(f'係数T0:::{T0}')




#if __name__ == '__main__'






    

        