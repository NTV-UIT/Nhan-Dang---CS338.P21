import React, { useState } from "react";
import {
  Box,
  Typography,
  Paper,
  Select,
  MenuItem,
  InputLabel,
  FormControl,
  TextField,
  Checkbox,
  FormControlLabel,
  Button,
  Slider,
  CircularProgress,
  IconButton,
  Dialog,
  DialogContent,
} from "@mui/material";
import PhotoCamera from "@mui/icons-material/PhotoCamera";
import DownloadIcon from "@mui/icons-material/Download";
import ZoomInIcon from "@mui/icons-material/ZoomIn";
import CloseIcon from "@mui/icons-material/Close";

const mapperOptions = [
  "afro", "angry", "Beyonce", "bobcut", "bowlcut", "curly hair",
  "Hilary Clinton", "Jhonny Depp", "mohawk", "purple hair", "surprised",
  "Taylor Swift", "trump", "Mark Zuckerberg",
];

export default function App() {
  const [method, setMethod] = useState("Optimization");
  const [experimentType, setExperimentType] = useState("edit");
  const [description, setDescription] = useState("");
  const [latentPath, setLatentPath] = useState("");
  const [latentFile, setLatentFile] = useState(null);
  const [optimizationSteps, setOptimizationSteps] = useState(40);
  const [l2Lambda, setL2Lambda] = useState(0.008);
  const [idLambda, setIdLambda] = useState(0.005);
  const [stylespace, setStylespace] = useState(false);
  const [createVideo, setCreateVideo] = useState(false);
  const [editType, setEditType] = useState("surprised");
  const [neutral, setNeutral] = useState("face with eyes");
  const [target, setTarget] = useState("face with blue eyes");
  const [beta, setBeta] = useState(0.15);
  const [alpha, setAlpha] = useState(-7.1);
  const [image, setImage] = useState(null);
  const [outputImage, setOutputImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [zoomOpen, setZoomOpen] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setLoading(true);
    setTimeout(() => {
      setOutputImage(
        image ||
          "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=600"
      );
      setLoading(false);
    }, 2000);
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setImage(URL.createObjectURL(file));
  };

  const handleLatentFileChange = (e) => {
    setLatentFile(e.target.files[0]);
    setLatentPath(e.target.files[0]?.name || "");
  };

  const renderOptimizationFields = () => (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
      <FormControl fullWidth size="small">
        <InputLabel>Experiment Type</InputLabel>
        <Select
          value={experimentType}
          label="Experiment Type"
          onChange={(e) => setExperimentType(e.target.value)}
        >
          <MenuItem value="edit">edit</MenuItem>
          <MenuItem value="free_generation">free_generation</MenuItem>
        </Select>
      </FormControl>
      <TextField
        label="Description"
        placeholder="A person with purple hair"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        fullWidth
        size="small"
      />
      <Box>
        <TextField
          label="Latent Path"
          value={latentPath}
          onChange={(e) => setLatentPath(e.target.value)}
          fullWidth
          size="small"
          sx={{ mb: 1 }}
        />
        <Button variant="outlined" component="label" size="small">
          Upload Latent File
          <input
            type="file"
            hidden
            accept=".npz,.npy"
            onChange={handleLatentFileChange}
          />
        </Button>
        {latentFile && (
          <Typography variant="caption" sx={{ ml: 1 }}>
            {latentFile.name}
          </Typography>
        )}
      </Box>
      <TextField
        label="Optimization Steps"
        type="number"
        value={optimizationSteps}
        onChange={(e) => setOptimizationSteps(Number(e.target.value))}
        fullWidth
        size="small"
        inputProps={{ min: 1, step: 1 }}
      />
      <TextField
        label="L2 Lambda"
        type="number"
        value={l2Lambda}
        onChange={(e) => setL2Lambda(Number(e.target.value))}
        fullWidth
        size="small"
        inputProps={{ step: 0.001, min: 0 }}
      />
      <TextField
        label="ID Lambda"
        type="number"
        value={idLambda}
        onChange={(e) => setIdLambda(Number(e.target.value))}
        fullWidth
        size="small"
        inputProps={{ step: 0.001, min: 0 }}
      />
      <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
        <FormControlLabel
          control={
            <Checkbox
              checked={stylespace}
              onChange={(e) => setStylespace(e.target.checked)}
              size="small"
            />
          }
          label="Edit StyleSpace"
        />
        <FormControlLabel
          control={
            <Checkbox
              checked={createVideo}
              onChange={(e) => setCreateVideo(e.target.checked)}
              size="small"
            />
          }
          label="Create Video"
        />
      </Box>
    </Box>
  );

  const renderMapperFields = () => (
    <Box>
      <FormControl fullWidth size="small">
        <InputLabel>Edit Type</InputLabel>
        <Select
          value={editType}
          label="Edit Type"
          onChange={(e) => setEditType(e.target.value)}
        >
          {mapperOptions.map((opt) => (
            <MenuItem key={opt} value={opt}>
              {opt}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    </Box>
  );

  const renderGlobalDirectionsFields = () => (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
      <TextField
        label="Neutral"
        value={neutral}
        onChange={(e) => setNeutral(e.target.value)}
        fullWidth
        size="small"
      />
      <TextField
        label="Target"
        value={target}
        onChange={(e) => setTarget(e.target.value)}
        fullWidth
        size="small"
      />
      <Box>
        <Typography gutterBottom fontSize={14}>Beta ({beta})</Typography>
        <Slider
          value={beta}
          min={0.08}
          max={0.3}
          step={0.01}
          onChange={(_, v) => setBeta(v)}
          valueLabelDisplay="auto"
          size="small"
        />
      </Box>
      <Box>
        <Typography gutterBottom fontSize={14}>Alpha ({alpha})</Typography>
        <Slider
          value={alpha}
          min={-10}
          max={10}
          step={0.1}
          onChange={(_, v) => setAlpha(v)}
          valueLabelDisplay="auto"
          size="small"
        />
      </Box>
    </Box>
  );

  // Layout: Left nửa màn hình, frame ảnh input chiếm 50% chiều cao bên trái
  return (
    <Box
      sx={{
        width: "100vw",
        height: "100vh",
        minHeight: 500,
        bgcolor: "#f3f4f8",
        overflow: "hidden",
      }}
    >
      <Box
        sx={{
          width: "100vw",
          height: "100vh",
          display: "flex",
          flexDirection: "row",
        }}
      >
        {/* Left Half: Input Image + Parameters */}
        <Box
          sx={{
            flex: 1, // <-- giữ nguyên
            minWidth: 0,
            p: 2,
            display: "flex",
            flexDirection: "column",
            borderRight: "1.5px solid #e0e0e0",
            bgcolor: "#f8fafc",
            height: "100vh",
            gap: 2,
          }}
        >
          {/* Frame: Ảnh đầu vào - chiếm đúng 50% chiều cao nửa trái */}
          <Paper
            elevation={3}
            sx={{
              flex: "0 0 50%",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              height: "calc(50vh - 24px)", // Trừ padding
              mb: 1,
              p: 1.5,
            }}
          >
            <Typography variant="h6" sx={{ mb: 1, fontSize: 18 }}>
              Ảnh đầu vào
            </Typography>
            <Button
              variant="contained"
              component="label"
              startIcon={<PhotoCamera />}
              size="small"
              sx={{ mb: 1 }}
            >
              Upload Image
              <input
                type="file"
                accept="image/jpeg, image/png"
                hidden
                onChange={handleImageChange}
              />
            </Button>
            <Box
              sx={{
                width: "100%",
                height: "calc(50vh - 100px)",
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                background: "#f4f5f7",
                borderRadius: 2,
                border: "1px solid #eee",
                overflow: "hidden",
                mt: 1,
              }}
            >
              {image ? (
                <img
                  src={image}
                  alt="input"
                  style={{
                    maxHeight: "100%",
                    maxWidth: "98%",
                    borderRadius: 8,
                    objectFit: "contain",
                  }}
                />
              ) : (
                <Typography variant="body2" color="text.secondary">
                  Chưa có ảnh đầu vào
                </Typography>
              )}
            </Box>
          </Paper>
          {/* Frame: Parameters and Method */}
          <Paper
            elevation={2}
            sx={{
              flex: "1 1 0",
              display: "flex",
              flexDirection: "column",
              gap: 1,
              minHeight: 60,
              overflowY: "auto",
              p: 1.5,
            }}
          >
            <form onSubmit={handleSubmit}>
              <FormControl fullWidth size="small" sx={{ mb: 1 }}>
                <InputLabel>Generation Method</InputLabel>
                <Select
                  value={method}
                  label="Generation Method"
                  onChange={(e) => setMethod(e.target.value)}
                >
                  <MenuItem value="Optimization">Optimization</MenuItem>
                  <MenuItem value="Mapper">Mapper</MenuItem>
                  <MenuItem value="Global Directions">
                    Global Directions
                  </MenuItem>
                </Select>
              </FormControl>
              <Box>
                <Typography variant="subtitle1" sx={{ mb: 1, fontSize: 16 }}>
                  Tham số
                </Typography>
                {method === "Optimization" && renderOptimizationFields()}
                {method === "Mapper" && renderMapperFields()}
                {method === "Global Directions" &&
                  renderGlobalDirectionsFields()}
              </Box>
              <Button
                variant="contained"
                type="submit"
                size="small"
                fullWidth
                disabled={loading}
                sx={{ mt: 1 }}
              >
                {loading ? <CircularProgress size={18} /> : "Chạy StyleCLIP"}
              </Button>
            </form>
          </Paper>
        </Box>
        {/* Right Half: Output Image */}
        <Box
          sx={{
            flex: 3, // <-- đổi từ 1 thành 3 để chiếm 3/4 chiều ngang
            p: 2,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            height: "100vh",
            justifyContent: "center",
            overflow: "hidden",
          }}
        >
          <Paper
            elevation={4}
            sx={{
              width: "100%",
              height: "90vh",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              bgcolor: "#fff",
              justifyContent: "center",
              p: 2,
            }}
          >
            <Typography variant="h5" sx={{ mb: 1, fontSize: 22 }}>
              Ảnh đầu ra
            </Typography>
            <Box
              sx={{
                width: "100%",
                height: "80vh",
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                position: "relative",
                background: "#f4f5f7",
                borderRadius: 2,
                border: "1px solid #eee",
                overflow: "hidden",
              }}
            >
              {loading ? (
                <CircularProgress size={38} />
              ) : outputImage ? (
                <Box sx={{ position: "relative", width: "100%", height: "100%" }}>
                  <img
                    src={outputImage}
                    alt="output"
                    style={{
                      maxHeight: "76vh",
                      maxWidth: "98%",
                      borderRadius: 8,
                      objectFit: "contain",
                      boxShadow: "0 2px 12px rgba(0,0,0,0.08)",
                      cursor: "zoom-in",
                      margin: "0 auto",
                      display: "block",
                    }}
                    onClick={() => setZoomOpen(true)}
                  />
                  <Box
                    sx={{
                      position: "absolute",
                      top: 8,
                      right: 8,
                      display: "flex",
                      gap: 1,
                    }}
                  >
                    <IconButton
                      color="primary"
                      onClick={() => setZoomOpen(true)}
                      size="small"
                      aria-label="Zoom"
                    >
                      <ZoomInIcon />
                    </IconButton>
                    <IconButton
                      color="primary"
                      aria-label="Download"
                      component="a"
                      href={outputImage}
                      download="styleclip_output.png"
                      size="small"
                    >
                      <DownloadIcon />
                    </IconButton>
                  </Box>
                </Box>
              ) : (
                <Typography variant="body1" color="text.secondary">
                  Ảnh đầu ra sẽ hiển thị ở đây
                </Typography>
              )}
            </Box>
          </Paper>
        </Box>
      </Box>
      {/* Zoom Dialog */}
      <Dialog open={zoomOpen} onClose={() => setZoomOpen(false)} maxWidth="md">
        <DialogContent sx={{ position: "relative", p: 0 }}>
          <IconButton
            onClick={() => setZoomOpen(false)}
            sx={{
              position: "absolute",
              top: 16,
              right: 16,
              background: "white",
              zIndex: 10,
            }}
          >
            <CloseIcon />
          </IconButton>
          {outputImage && (
            <img
              src={outputImage}
              alt="Zoomed output"
              style={{
                maxWidth: "90vw",
                maxHeight: "80vh",
                display: "block",
                margin: "auto",
              }}
            />
          )}
        </DialogContent>
      </Dialog>
    </Box>
  );
}