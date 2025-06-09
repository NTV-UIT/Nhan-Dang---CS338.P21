import React, { useState } from "react";
import { Box, Typography, Button, CircularProgress, Paper, FormControl, InputLabel, Select, MenuItem, IconButton, Dialog, DialogContent } from "@mui/material";
import PhotoCamera from "@mui/icons-material/PhotoCamera";
import DownloadIcon from "@mui/icons-material/Download";
import ZoomInIcon from "@mui/icons-material/ZoomIn";
import CloseIcon from "@mui/icons-material/Close";

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

  // Xử lý upload ảnh
  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setImage(URL.createObjectURL(file));
    setImageFile(file);
    setOutputImage(null);
    setOriginalImage(null);
    setError("");
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
            <FormControl fullWidth size="small" sx={{ mb: 2 }}>
              <InputLabel>Kiểu tóc</InputLabel>
              <Select value={editType} label="Kiểu tóc" onChange={(e) => setEditType(e.target.value)}>
                {mapperOptions.map((opt) => (
                  <MenuItem key={opt} value={opt}>{opt}</MenuItem>
                ))}
              </Select>
            </FormControl>
            <Button variant="contained" type="submit" size="small" fullWidth disabled={processing || !imageFile} sx={{ mb: 1 }}>
              {processing ? <CircularProgress size={18} /> : "Chạy StyleCLIP"}
            </Button>
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