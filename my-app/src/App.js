import React, { useState, useEffect } from "react";
import { Box, Typography, Button, CircularProgress, Paper, FormControl, InputLabel, Select, MenuItem, IconButton, Dialog, DialogContent, Rating, Divider, Radio, RadioGroup, FormControlLabel, FormLabel } from "@mui/material";
import PhotoCamera from "@mui/icons-material/PhotoCamera";
import DownloadIcon from "@mui/icons-material/Download";
import ZoomInIcon from "@mui/icons-material/ZoomIn";
import CloseIcon from "@mui/icons-material/Close";
import StarIcon from "@mui/icons-material/Star";
import CropDialog from "./CropDialog";

const mapperOptions = [
  "afro", "bobcut", "bowlcut", "curly_hair", "mohawk", "purple_hair"
];

export default function App() {
  const [editType, setEditType] = useState("afro");
  const [image, setImage] = useState(null);
  const [imageFile, setImageFile] = useState(null);
  const [outputImage, setOutputImage] = useState(null);
  const [originalImage, setOriginalImage] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState("");
  const [zoomOpen, setZoomOpen] = useState(false);
  
  // Rating states
  const [ratings, setRatings] = useState({});
  const [userRating, setUserRating] = useState(0);
  const [showRating, setShowRating] = useState(false);

  // Crop states
  const [cropOpen, setCropOpen] = useState(false);
  const [cropImage, setCropImage] = useState(null);
  const [originalImageFile, setOriginalImageFile] = useState(null);
  const [originalImageUrl, setOriginalImageUrl] = useState(null);
  const [inputImageType, setInputImageType] = useState("cropped"); // "cropped" hoặc "original"

  // Load ratings from localStorage
  useEffect(() => {
    const savedRatings = localStorage.getItem('styleclip_ratings');
    if (savedRatings) {
      setRatings(JSON.parse(savedRatings));
    }
  }, []);

  // Save ratings to localStorage
  const saveRatings = (newRatings) => {
    setRatings(newRatings);
    localStorage.setItem('styleclip_ratings', JSON.stringify(newRatings));
  };

  // Calculate average rating for a specific hair style
  const getAverageRating = (hairStyle) => {
    const styleRatings = ratings[hairStyle];
    if (!styleRatings || styleRatings.length === 0) return 0;
    const sum = styleRatings.reduce((acc, rating) => acc + rating, 0);
    return Math.round((sum / styleRatings.length) * 100) / 100;
  };

  // Calculate overall average rating
  const getOverallAverageRating = () => {
    let totalSum = 0;
    let totalCount = 0;
    
    Object.values(ratings).forEach(styleRatings => {
      if (styleRatings && styleRatings.length > 0) {
        totalSum += styleRatings.reduce((acc, rating) => acc + rating, 0);
        totalCount += styleRatings.length;
      }
    });
    
    return totalCount > 0 ? Math.round((totalSum / totalCount) * 100) / 100 : 0;
  };

  // Submit user rating
  const handleRatingSubmit = () => {
    if (userRating === 0) return;
    
    const newRatings = { ...ratings };
    if (!newRatings[editType]) {
      newRatings[editType] = [];
    }
    newRatings[editType].push(userRating);
    
    saveRatings(newRatings);
    setUserRating(0);
    setShowRating(false);
  };

  // Xử lý upload ảnh
  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const url = URL.createObjectURL(file);
    setCropImage(url);
    setCropOpen(true);
    setOriginalImageFile(file);
    setOriginalImageUrl(url);
    setOutputImage(null);
    setOriginalImage(null);
    setError("");
    setInputImageType("cropped");
  };

  // Sau khi crop xong
  const handleCropDone = (blob, fileUrl) => {
    setImage(fileUrl);
    setImageFile(new File([blob], "cropped.jpeg", { type: "image/jpeg" }));
  };

  // Khi chọn loại ảnh đầu vào
  const handleInputImageTypeChange = (e) => {
    setInputImageType(e.target.value);
    if (e.target.value === "original") {
      setImage(originalImageUrl);
      setImageFile(originalImageFile);
    }
    // Nếu chọn cropped, giữ nguyên image & imageFile hiện tại (đã crop)
  };

  // Gửi request tới /mapper
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!imageFile) return;
    setProcessing(true);
    setError("");
    setOutputImage(null);
    setOriginalImage(null);
    try {
      const formData = new FormData();
      formData.append("image", imageFile);
      formData.append("function", editType);
      const res = await fetch("http://localhost:8000/mapper/", {
        method: "POST",
        body: formData,
      });
      let data;
      let text = await res.text();
      console.log("[DEBUG] Raw response text:", text);
      try {
        data = JSON.parse(text);
      } catch (jsonErr) {
        setError("Lỗi khi đọc dữ liệu trả về từ server.");
        setProcessing(false);
        return;
      }
      console.log("[DEBUG] Parsed response:", data);
      if (res.ok && data.modified_image && data.original_image) {
        setOutputImage(`data:image/png;base64,${data.modified_image}`);
        setOriginalImage(`data:image/png;base64,${data.original_image}`);
        setShowRating(true); // Show rating after successful generation
      } else {
        setError(data.message || "Có lỗi xảy ra khi xử lý ảnh.");
      }
    } catch (err) {
      setError("Không thể kết nối tới server hoặc lỗi mạng.");
    } finally {
      setProcessing(false);
    }
  };

  return (
    <Box sx={{ width: "100vw", minHeight: "100vh", bgcolor: "#f3f4f8", p: 2 }}>
      {/* <Typography variant="h4" sx={{ mb: 2, textAlign: "center" }}>Demo chỉnh sửa kiểu tóc StyleCLIP</Typography> */}
      <Box sx={{ display: "flex", flexDirection: { xs: "column", md: "row" }, gap: 4, justifyContent: "center", alignItems: "flex-start", height: "80vh" }}>
        {/* Bên trái: chức năng và ảnh gốc */}
        <Paper sx={{ p: 3, minWidth: 320, maxWidth: 400, flex: "0 0 350px", display: "flex", flexDirection: "column", alignItems: "center", height: "100%" }} elevation={3}>
          <form onSubmit={handleSubmit} style={{ width: "100%" }}>
            <Button variant="contained" component="label" startIcon={<PhotoCamera />} size="small" fullWidth sx={{ mb: 2 }}>
              Upload Image
              <input type="file" accept="image/jpeg, image/png" hidden onChange={handleImageChange} />
            </Button>
            {/* Nút cắt ảnh */}
            {image && (
              <Button variant="outlined" size="small" fullWidth sx={{ mb: 2 }} onClick={() => setCropOpen(true)}>
                Cắt ảnh về hình vuông
              </Button>
            )}
            {/* Chọn loại ảnh đầu vào */}
            {image && originalImageUrl && (
              <Box sx={{ mb: 2 }}>
                <FormLabel component="legend">Chọn ảnh đầu vào</FormLabel>
                <RadioGroup
                  row
                  value={inputImageType}
                  onChange={handleInputImageTypeChange}
                  name="input-image-type"
                >
                  <FormControlLabel value="cropped" control={<Radio />} label="Ảnh đã cắt" />
                  <FormControlLabel value="original" control={<Radio />} label="Ảnh gốc" />
                </RadioGroup>
              </Box>
            )}
            <FormControl fullWidth size="small" sx={{ mb: 2 }}>
              <InputLabel>Kiểu tóc</InputLabel>
              <Select value={editType} label="Kiểu tóc" onChange={(e) => setEditType(e.target.value)}>
                {mapperOptions.map((opt) => (
                  <MenuItem key={opt} value={opt}>
                    {opt} ({getAverageRating(opt)}/10 ⭐)
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <Button variant="contained" type="submit" size="small" fullWidth disabled={processing || !imageFile} sx={{ mb: 2 }}>
              {processing ? <CircularProgress size={18} /> : "Chạy StyleCLIP"}
            </Button>
            
            {/* Rating Section */}
            <Paper sx={{ p: 2, mb: 2, bgcolor: "#f9f9f9" }} elevation={1}>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>📊 Độ đo đánh giá</Typography>
              <Typography variant="body2" sx={{ mb: 1 }}>
                <strong>{editType}:</strong> {getAverageRating(editType)}/10 
                {ratings[editType] && ` (${ratings[editType].length} votes)`}
              </Typography>
              <Typography variant="body2" sx={{ mb: 1 }}>
                <strong>Tổng thể:</strong> {getOverallAverageRating()}/10
              </Typography>
              
              {showRating && (
                <Box sx={{ mt: 2, textAlign: "center" }}>
                  <Typography variant="body2" sx={{ mb: 1 }}>Đánh giá kết quả:</Typography>
                  <Rating
                    name="user-rating"
                    value={userRating}
                    onChange={(_, newValue) => setUserRating(newValue)}
                    max={10}
                    size="small"
                    icon={<StarIcon fontSize="inherit" />}
                    emptyIcon={<StarIcon fontSize="inherit" />}
                  />
                  <Box sx={{ mt: 1 }}>
                    <Button size="small" variant="outlined" onClick={handleRatingSubmit} disabled={userRating === 0}>
                      Gửi đánh giá
                    </Button>
                    <Button size="small" onClick={() => setShowRating(false)} sx={{ ml: 1 }}>
                      Bỏ qua
                    </Button>
                  </Box>
                </Box>
              )}
            </Paper>

            {error && (
              <Typography color="error" sx={{ mt: 1 }}>{error}</Typography>
            )}
          </form>
          {/* Hiển thị ảnh đã chọn với kích thước lớn hơn */}
          {image && (
            <Box sx={{ mt: 3, textAlign: "center", width: "100%" }}>
              <Typography variant="subtitle2">Ảnh đã chọn</Typography>
              <img src={image} alt="input" style={{ maxHeight: 400, maxWidth: 320, borderRadius: 12, objectFit: "contain", margin: "0 8px" }} />
            </Box>
          )}
        </Paper>
        {/* Bên phải: ảnh gen ra */}
        <Paper sx={{ p: 3, flex: 1, minWidth: 320, display: "flex", flexDirection: "column", alignItems: "center", height: "100%", bgcolor: "#fff" }} elevation={3}>
          <Typography variant="h6" sx={{ mb: 2 }}>Ảnh đã chỉnh sửa</Typography>
          {outputImage ? (
            <>
              <img src={outputImage} alt="output" style={{ maxHeight: 600, maxWidth: 480, borderRadius: 12, objectFit: "contain", margin: "0 8px", cursor: "zoom-in" }} onClick={() => setZoomOpen(true)} />
              <Box sx={{ mt: 2 }}>
                <IconButton color="primary" aria-label="Download" component="a" href={outputImage} download="styleclip_output.png" size="large"><DownloadIcon /></IconButton>
                <IconButton color="primary" aria-label="Zoom" onClick={() => setZoomOpen(true)} size="large"><ZoomInIcon /></IconButton>
              </Box>
            </>
          ) : (
            <Box sx={{ width: 320, height: 400, border: "2px dashed #ccc", borderRadius: 12, display: "flex", alignItems: "center", justifyContent: "center", color: "#bbb" }}>
              <Typography variant="body2">Chưa có ảnh kết quả</Typography>
            </Box>
          )}
        </Paper>
      </Box>
      {/* Crop Dialog */}
      <CropDialog
        open={cropOpen}
        imageSrc={cropImage || image}
        onClose={() => setCropOpen(false)}
        onCropDone={handleCropDone}
      />
      {/* Zoom Dialog */}
      <Dialog open={zoomOpen} onClose={() => setZoomOpen(false)} maxWidth="md">
        <DialogContent sx={{ position: "relative", p: 0 }}>
          <IconButton onClick={() => setZoomOpen(false)} sx={{ position: "absolute", top: 16, right: 16, background: "white", zIndex: 10 }}><CloseIcon /></IconButton>
          {outputImage && <img src={outputImage} alt="Zoomed output" style={{ maxWidth: "90vw", maxHeight: "80vh", display: "block", margin: "auto" }} />}
        </DialogContent>
      </Dialog>
    </Box>
  );
}