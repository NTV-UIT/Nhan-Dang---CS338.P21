<!-- Banner -->
<p align="center">
  <a href="https://www.uit.edu.vn/" title="Trường Đại học Công nghệ Thông tin" style="border: none;">
    <img src="https://i.imgur.com/WmMnSRt.png" alt="Trường Đại học Công nghệ Thông tin | University of Information Technology">
  </a>
</p>

<h1 align="center"><b>Nhận Dạng</b></h1>

<div align="center">
  <table>
    <thead>
      <tr>
        <th>STT</th>
        <th>MSSV</th>
        <th>Họ và Tên</th>
        <th>Chức vụ</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>1</td>
        <td>22520775</td>
        <td>Nguyễn Xuân Linh</td>
        <td>Nhóm trưởng</td>
      </tr>
      <tr>
        <td>2</td>
        <td>22521677</td>
        <td>Nguyễn Thế Vĩnh</td>
        <td>Thành viên</td>
      </tr>
      <tr>
        <td>3</td>
        <td>22521671</td>
        <td>Lưu Khánh Vinh</td>
        <td>Thành viên</td>
      </tr>
    </tbody>
  </table>
</div>

# GIỚI THIỆU KHÓA HỌC
* **Tên Khóa Học:** Nhận Dạng.
* **Mã Lớp:** CS338.P21.
* **Năm Học:** HK2 (2024 - 2025).
* **Giảng Viên**: TS Dương Việt Hằng, Trần Doãn Thuyên

## Tóm tắt đồ án

Đồ án xây dựng ứng dụng chỉnh sửa ảnh khuôn mặt, tập trung vào thay đổi kiểu tóc dựa trên mô tả văn bản tự nhiên. Hệ thống sử dụng StyleCLIP (kết hợp StyleGAN và CLIP) để điều khiển ảnh sinh ra bằng ngôn ngữ. Sau khi thử nghiệm nhiều phương pháp, nhóm chọn và cải tiến Latent Mapper để nâng cao chất lượng và tốc độ phản hồi khi chỉnh sửa. Ứng dụng cho phép người dùng tải ảnh, chọn kiểu tóc mong muốn và nhận kết quả chỉnh sửa nhanh, chính xác.

# Hướng dẫn cài đặt & sử dụng dự án StyleCLIP

## 1. Cấu trúc thư mục
```
Nhan-Dang---CS338.P21/
├── backend/
│   ├── app/
│   │   ├── StyleCLIP/
│   │   │   ├── mapper/
│   │   │   │   ├── scripts/
│   │   │   │   │   └── results/
│   │   │   │   │       └── evaluation_results/
│   │   │   │   └── models/
│   │   │   └── global_direction/
│   │   ├── encoder4editing/
│   │   ├── stylegan2/
│   │   ├── apis/
│   │   ├── templates/
│   │   ├── static/
│   │   ├── results/
│   │   ├── main.py
│   │   ├── setup.sh
│   │   └── requirements.txt
│   ├── pretrained_models/
│   └── down_ckp.sh
├── my-app/
│   ├── src/
│   ├── public/
│   └── package.json
└── README.md
```

### 1.1. Mô tả các thư mục chính
- **backend/app/StyleCLIP/**: Chứa mã nguồn chính của mô hình StyleCLIP
- **backend/app/encoder4editing/**: Mã nguồn cho encoder E4E
- **backend/app/stylegan2/**: Mã nguồn cho mô hình StyleGAN2
- **backend/app/apis/**: Chứa các API endpoints
- **backend/app/templates/**: Chứa các template HTML
- **backend/app/static/**: Chứa các file tĩnh (CSS, JS, images)
- **backend/app/results/**: Thư mục lưu kết quả
- **backend/pretrained_models/**: Chứa các mô hình đã được huấn luyện
- **my-app/**: Mã nguồn frontend React

## 2. Kết quả đánh giá mô hình

### 2.1. So sánh mô hình cũ và mới

<div align="center">

| Độ đo                  | Mô hình cũ   | Mô hình mới   |
|------------------------|--------------|--------------|
| CLIP Similarity ↑      | **27.7237**  | 26.5917      |
| ΔCLIP ↑                | 0.1540       | **0.1720**   |
| LPIPS (vs original) ↓  | 0.1857       | **0.1728**   |
| FID (vs original) ↓    | 0.7745       | **0.6210**   |

</div>

**Bảng 1:** Kết quả đánh giá chi tiết giữa mô hình cũ và mô hình mới. ↑: giá trị càng cao càng tốt, ↓: giá trị càng thấp càng tốt.

### 2.2. Phương pháp đánh giá

#### 2.2.1. Độ đo kỹ thuật
1. **CLIP Similarity**: Đo lường độ tương đồng ngữ nghĩa giữa ảnh kết quả và prompt text
2. **LPIPS**: Đánh giá sự khác biệt về mặt thị giác giữa các ảnh
3. **FID**: Đo lường chất lượng và tính đa dạng của ảnh được tạo ra
4. **Delta CLIP**: Đánh giá mức độ thay đổi so với ảnh gốc

#### 2.2.2. Độ đo đánh giá người dùng
5. **USS (User Satisfaction Score)**: Điểm hài lòng trung bình cho từng kiểu tóc (0-10)
6. **OUSS (Overall User Satisfaction Score)**: Điểm hài lòng tổng thể hệ thống (0-10)

### 2.3. Cách chạy đánh giá mô hình

Để đánh giá và so sánh hai mô hình Latent Mapper (cũ và mới), sử dụng script sau:

```bash
cd backend/app/StyleCLIP/mapper/scripts
python evaluate_mappers.py
```

- Kết quả đánh giá (bao gồm các chỉ số và hình ảnh so sánh) sẽ được lưu trong thư mục:
  `backend/app/StyleCLIP/mapper/scripts/results/evaluation_results/`

## 3. Yêu cầu hệ thống
- Đã cài đặt Anaconda hoặc Miniconda
- GPU NVIDIA hỗ trợ CUDA (khuyến nghị)
- Python >= 3.9 ( Tôi sử dụng 3.12.7)
- Node.js >= 16.x (để chạy giao diện web frontend) ( Tôi sử dụng v18.19.1)

## 4. Cài đặt mô hình và phụ thuộc

### 4.1. Tải checkpoints
```bash
cd Nhan-Dang---CS338.P21/backend
mkdir pretrained_models && ./down_ckp.sh
```

### 4.2. Tạo và kích hoạt môi trường conda
```bash
conda create -n styleclip python=3.12.7
conda activate styleclip
```

### 4.3. Cài đặt PyTorch (có CUDA)
- Kiểm tra phiên bản CUDA:
```bash
nvcc --version
```
- Cài đặt PyTorch phù hợp (ví dụ với CUDA 12.4):
```bash
conda install pytorch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 pytorch-cuda=12.4 -c pytorch -c nvidia
```

### 4.4. Cài đặt TensorFlow
```bash
python -m pip install tensorflow==2.17.1
```

### 4.5. Cài đặt các thư viện bổ sung
```bash
python -m pip install -r backend/app/requirements.txt
```

### 4.6. Kiểm tra CUDA cho PyTorch & TensorFlow (tuỳ chọn)
```bash
python -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('CUDA version:', torch.version.cuda if torch.cuda.is_available() else 'Not available')"
python -c "import tensorflow as tf; print('GPU available:', tf.config.list_physical_devices('GPU')); print('TensorFlow version:', tf.__version__)"
```

### 4.7. Cài đặt ninja (Linux)
```bash
wget https://github.com/ninja-build/ninja/releases/download/v1.8.2/ninja-linux.zip
sudo unzip ninja-linux.zip -d /usr/local/bin/
sudo update-alternatives --install /usr/bin/ninja ninja /usr/local/bin/ninja 1 --force
```

### 4.8. Cài đặt dlib (Linux)
```bash
python -m pip install --upgrade pip
python -m pip install cmake dlib
```
- Nếu gặp lỗi, tham khảo: [Dlib_Windows_Python3.x](https://github.com/z-mahmud22/Dlib_Windows_Python3.x)

## 5. Chạy backend (FastAPI)
```bash
cd backend/app
python -m uvicorn main:app --reload --port 8000
```

## 6. Chạy frontend (React)
```bash
cd my-app
npm install
npm start
```
- Giao diện sẽ chạy tại: http://localhost:3000

## 6.1. Triển khai với Docker (Khuyến nghị)

### 6.1.1. Yêu cầu Docker
- Docker >= 20.10
- Docker Compose >= 2.0
- NVIDIA Docker (cho GPU support)

### 6.1.2. Kiểm tra yêu cầu hệ thống
```bash
# Kiểm tra Docker
docker --version
docker-compose --version

# Kiểm tra NVIDIA Docker (nếu có GPU)
docker run --rm --gpus all nvidia/cuda:12.4-base nvidia-smi
```

### 6.1.3. Triển khai tự động (Khuyến nghị)
```bash
# Cấp quyền thực thi
chmod +x docker-deploy.sh

# Triển khai hoàn chỉnh (tự động download models, build và start)
./docker-deploy.sh deploy
```

### 6.1.4. Các lệnh Docker khác
```bash
# Chỉ kiểm tra requirements
./docker-deploy.sh check

# Chỉ download pretrained models
./docker-deploy.sh setup

# Chỉ build images
./docker-deploy.sh build

# Start với docker-compose
docker-compose up -d
```

### 6.1.5. Build thủ công (nếu cần)
```bash
# Download pretrained models
cd backend && ./down_ckp.sh && cd ..

# Build backend image
docker build -f backend/Dockerfile -t styleclip-backend:latest .

# Build frontend image  
docker build -f frontend/Dockerfile -t styleclip-frontend:latest .

# Start với docker-compose
docker-compose up -d
```

### 6.1.6. Truy cập ứng dụng Docker
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000  
- **Nginx Proxy**: http://localhost:80 (tất cả services qua 1 port)

### 6.1.7. Troubleshooting Docker
```bash
# Xem logs chi tiết
docker-compose logs backend
docker-compose logs frontend

# Restart service cụ thể
docker-compose restart backend

# Kiểm tra container status
docker ps

# Vào container để debug
docker exec -it styleclip-backend bash
```

## 7. Sử dụng
- Truy cập http://localhost:3000 trên trình duyệt.
- Tải ảnh lên, chọn kiểu tóc và nhấn "Chạy StyleCLIP" để nhận kết quả.
- Sau khi tạo ảnh thành công, bạn có thể đánh giá kết quả từ 1-10 sao để cải thiện chất lượng dịch vụ.

### 7.1. Tính năng đánh giá người dùng
Ứng dụng tích hợp hệ thống đánh giá người dùng với các tính năng sau:

#### 📊 **Độ đo đánh giá**
- **USS (User Satisfaction Score)**: Điểm hài lòng riêng cho từng kiểu tóc
- **OUSS (Overall User Satisfaction Score)**: Điểm hài lòng tổng thể của hệ thống
- Thang điểm: 1-10 sao với độ chính xác 2 chữ số thập phân

#### 🌟 **Cách sử dụng**
1. Sau khi tạo ảnh thành công, giao diện sẽ hiển thị form đánh giá
2. Chọn số sao từ 1-10 để đánh giá chất lượng kết quả
3. Nhấn "Gửi đánh giá" để lưu feedback hoặc "Bỏ qua" để tiếp tục

#### 📈 **Hiển thị thống kê**
- Điểm trung bình cho từng kiểu tóc hiển thị trong dropdown selection
- Số lượng votes cho mỗi kiểu tóc
- Điểm tổng thể của toàn hệ thống
- Dữ liệu được cập nhật realtime khi có đánh giá mới

#### 💾 **Lưu trữ dữ liệu**
- Dữ liệu đánh giá được lưu trong localStorage của trình duyệt
- Không cần đăng nhập hoặc tạo tài khoản
- Dữ liệu được bảo tồn giữa các phiên sử dụng

## 8. Ghi chú
- Nếu backend chạy ở port khác, sửa lại URL API trong `my-app/src/App.js` cho phù hợp.
- Đảm bảo backend và frontend cùng chạy để sử dụng đầy đủ chức năng.

---

Nếu gặp lỗi hoặc cần hỗ trợ, hãy kiểm tra lại log terminal hoặc liên hệ người phát triển dự án.

| Kiểu tóc     | Số lượt đánh giá | Điểm trung bình (User Satisfaction Score) |
|-------------|------------------|-------------------------------------------|
| afro        | 50               | 8.12/10                                   |
| bobcut      | 50               | 7.98/10                                   |
| bowlcut     | 50               | 8.21/10                                   |
| curly_hair  | 50               | 7.87/10                                   |
| mohawk      | 50               | 8.05/10                                   |
| purple_hair | 50               | 8.09/10                                   |

**Trạng thái USS (User Satisfaction Score):** Đã có dữ liệu  
**Trạng thái OUSS (Overall User Satisfaction Score):** 8.05/10 (trung bình toàn bộ các kiểu tóc)

Bảng 2: Độ đo đánh giá người dùng được tích hợp trong ứng dụng web. Dữ liệu sẽ được cập nhật liên tục khi người dùng sử dụng ứng dụng.
