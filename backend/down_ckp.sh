#!/bin/bash
pip install gdown

# Tải các file
gdown --id 1N0MZSqPRJpLfP4mFQCS14ikrVSe8vQlL -O 'pretrained_models/model_ir_se50.pth'
gdown --id 1EM87UquaoQmk17Q8d5kYIAHqu0dkYqdT -O 'pretrained_models/stylegan2-ffhq-config-f.pt'
gdown --id 1F-mPrhO-UeWrV1QYMZck63R43aLtPChI -O 'pretrained_models/surprised.pt'
gdown --id 1VL3lP4avRhz75LxSza6jgDe-pHd2veQG -O 'pretrained_models/example_celebs.pt'
gdown --id 1j7RIfmrCoisxx3t-r-KC02Qc8barBecr -O 'pretrained_models/test_faces.pt'
