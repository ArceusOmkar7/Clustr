
# 🧭 CLUSTR – MVP Development Roadmap

## 🧩 Overview

**CLUSTR** helps users automatically organize photo albums using:

- Scene understanding (image captioning via BLIP)
- Unique face detection and clustering (via MTCNN + FaceNet + DBSCAN)

---

## 🟦 **Phase 1: Project Setup & Image Upload Pipeline | Completed ✅**

### 🔹 Objective:

Create a working frontend-backend pipeline for users to upload and store photos.

### 🔧 Tasks:

- **Frontend** (React + Tailwind):
    - Image upload UI with drag & drop or file picker
    - Upload status per image
    - Basic image grid to display uploaded previews
- **Backend** (FastAPI or Flask):
    - REST API for file upload
    - Save files with unique names (timestamp + hash or UUID)
    - Store metadata (filename, upload date) in SQLite or simple JSON

### ✅ Output:

- Upload images → save on disk → show preview in frontend.

---

## 🟦 **Phase 2: Image Captioning Integration**

### 🔹 Objective:

Add scene understanding to each photo using captions.

### 🔧 Tasks:

- Integrate BLIP model (`Salesforce/blip-image-captioning-base`)
- For each uploaded image:
    - Generate a caption (e.g., “Two people standing at the beach”)
    - Store alongside image path in DB/JSON
- Return captioned data to frontend:
    - Show caption below each image

### ✅ Output:

- Each uploaded image now has a semantic description visible in the UI.

---

## 🟦 **Phase 3: Face Detection & Clustering**

### 🔹 Objective:

Identify unique people in photos by detecting and clustering faces.

### 🔧 Tasks:

- Use **MTCNN** to detect faces
- Use **FaceNet** to generate a 128-D face embedding per face
- Store: image ID, face crop (optional), embedding
- Cluster faces across all images using **DBSCAN** or **K-Means**:
    - Each face gets assigned a **person ID**
    - Save face cluster ID per image

### ✅ Output:

- Faces across multiple images grouped as unique persons.
- Each image now links to one or more person IDs.

---

## 🟦 **Phase 4: Album Generation & Display**

### 🔹 Objective:

Create and display photo albums organized by **scene** and **people**.

### 🔧 Tasks:

- **Event Albums**:
    - Parse key nouns/phrases from captions (e.g., “beach”, “birthday”, “family”)
    - Group images with similar keywords
- **People Albums**:
    - For each face cluster ID, group all matching images
    - Display face albums like: “Person 1”, “Person 2”
- **Frontend UI**:
    - Toggle between “All Photos”, “By Scene”, “By People”
    - Grid layout for each album
    - Basic search bar (caption keyword or person ID)

### ✅ Output:

- Functional albums automatically grouped by:
    - Event type (scene keyword)
    - Person (clustered face)

---

# 🧱 Backend Summary

| Module | Technology |
| --- | --- |
| API Server | FastAPI or Flask |
| Image Storage | Local (or Cloud) |
| Metadata DB | SQLite / JSON |
| Captioning | BLIP (HuggingFace) |
| Face Model | MTCNN + FaceNet |
| Clustering | DBSCAN |

---

# 🌿 Post-MVP Enhancements (Future Phases)

| Feature | Benefit |
| --- | --- |
| Name tagging for faces | Let users label people ("Mom", "Me") |
| Persistent recognition | Auto-tag people in new uploads |
| Multi-user login system | Isolate galleries per user |
| CLIP-powered search | “Me at a concert” → returns matches |
| Cloud storage (S3/Firebase) | Scalable image hosting |
| Video support | Keyframe extraction + same pipeline |

---
