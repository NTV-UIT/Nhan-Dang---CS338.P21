#!/bin/bash
pip install gdown
mkdir -p pretrained_models
# Tải các file
# gdown --id 1N0MZSqPRJpLfP4mFQCS14ikrVSe8vQlL -O 'pretrained_models/model_ir_se50.pth'
# gdown --id 1EM87UquaoQmk17Q8d5kYIAHqu0dkYqdT -O 'pretrained_models/stylegan2-ffhq-config-f.pt'
# gdown --id 1F-mPrhO-UeWrV1QYMZck63R43aLtPChI -O 'pretrained_models/surprised.pt'
# gdown --id 1VL3lP4avRhz75LxSza6jgDe-pHd2veQG -O 'pretrained_models/example_celebs.pt'
gdown --id 1j7RIfmrCoisxx3t-r-KC02Qc8barBecr -O 'pretrained_models/test_faces.pt'
gdown --id 1J8v8Y2aVNKBP1qup1ihlXwnDLjzaPIBf -O 'pretrained_models/afro.pt'
gdown --id 1z9SH69n1CHp9v1jpWNMOECuOM-NTeflt -O 'pretrained_models/bobcut.pt'
gdown --id 1nRV_ruKCMmvF_yejCrMoABc0cxtx1DFa -O 'pretrained_models/bowlcut.pt'
gdown --id 1jqxLvToQqc4fpG6gKSrDIf8qUxYd_V3I -O 'pretrained_models/curly_hair.pt'
gdown --id 1u-NROHYXMien3vXnAFIHVtmhaZ7SKhMB -O 'pretrained_models/mohawk.pt'
gdown --id 12bJQ9Cu4ZRIZvb6QOIESmQRT1YElJ9jU -O 'pretrained_models/purple_hair.pt'
gdown --id 1cUv_reLE6k3604or78EranS7XzuVMWeO -O 'pretrained_models/e4e_ffhq_encode.pt'
