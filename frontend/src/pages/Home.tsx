import { UploadComponent } from "../components/UploadComponent";
import type { UploadableFile } from "../types";

const Home = () => {
  const handleUploadComplete = (uploadedFiles: UploadableFile[]) => {
    console.log("Upload completed with files:", uploadedFiles);
  };

  return (
    <div className="container mx-auto py-6">
      <UploadComponent onUploadComplete={handleUploadComplete} />
    </div>
  );
};

export default Home;
