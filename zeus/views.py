from django.shortcuts import render
from django.core.files.storage import FileSystemStorage

from zeus.forms import uploadForm

import pandas as pd
import numpy as np
from androguard import misc
from tensorflow import keras

# Create your views here.
def index(request):
    return render(request, 'index.html')

def result(request):
    if request.method == 'POST':
        form = uploadForm(request.POST, request.FILES)

        if form.is_valid():
            file_input = request.FILES['file_input']
            fs = FileSystemStorage()
            file = fs.save('test.apk', file_input)

            # Extract APK File
            listOfInputApkPermission = [['File Name', 'Permission']]
            a, d, dx = misc.AnalyzeAPK(fs.path(file))
            app_name = a.get_app_name()
            input_apk_permission = a.get_permissions()
            listOfInputApkPermission.append((a.get_app_name(), ','.join(input_apk_permission)))
            headers = listOfInputApkPermission.pop(0)
            df = pd.DataFrame(listOfInputApkPermission, columns=headers)

            # Get and Check Permission
            data_test_detected = getTrainAndTestDataset(df)
            permission = df['Permission']

            # Prepare Data for test
            data_test_detected = data_test_detected.astype('float32')
            data_test_detected = np.array(data_test_detected)
            data_test_detected = data_test_detected.reshape(data_test_detected.shape[0], 13, 13, 1)

            # Test Data
            load_model = keras.models.load_model(fs.path('model_TA_03.h5'))
            result = load_model.predict_classes(data_test_detected)
            if result == 0:
                status = "Kurang Berbahaya"
            elif result == 1:
                status = "Berbahaya"
            else:
                status = "Tidak Berbahaya"


            fs.delete(file)
            return render(request, 'result.html', {'app_name': app_name,
                                                    'status': status,
                                                   'permission' : permission,
                                                    })


    return render(request, 'result.html')




# Function
def getTrainAndTestDataset(dfData):
    fs = FileSystemStorage()
    android_manifest_permission = pd.read_csv(fs.path('manifestPermissionAndroid.csv'))
    android_manifest_permission['class'] = 'Miscellaneous'
    android_groups_permission = pd.read_csv(fs.path('permissionGeneral.csv'))
    dfPermission = android_groups_permission.append(android_manifest_permission).drop_duplicates(subset='name').reset_index(drop=True)
    addNineRow = pd.DataFrame([[0], [0], [0], [0], [0], [0], [0], [0], [0]])
    addNineRow.columns = ['status']
    counter = 0
    data = dfData['Permission']
    data = data.fillna('')
    dataResult = pd.DataFrame()

    for row in data:
        dfAPKPermission = row.split(sep=',')
        dfAPKPermission = pd.DataFrame(dfAPKPermission)
        dfAPKPermission.columns = ['name']
        dfAPKPermission = dfPermission.name.isin(dfAPKPermission.name).astype(int).to_frame()
        dfAPKPermission.columns = ['status']
        dfAPKPermission = dfAPKPermission.append(addNineRow).reset_index(drop=True)
        dfAPKPermission = dfAPKPermission.transpose()
        dataResult = dataResult.append(dfAPKPermission)

    dataResult = dataResult.replace(1, 255).reset_index(drop=True)
    return dataResult