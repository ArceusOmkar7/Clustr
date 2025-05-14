export default function Gallery() {
  return (
    <div className="container mx-auto py-6">
      <h1 className="text-3xl font-bold">Gallery</h1>
      <p className="mt-4">View your gallery items here.</p>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-6">
        {/* Placeholder for gallery items */}
        {Array(6)
          .fill(0)
          .map((_, index) => (
            <div
              key={index}
              className="bg-card text-card-foreground rounded-lg p-4 h-48 flex items-center justify-center"
            >
              Gallery Item {index + 1}
            </div>
          ))}
      </div>
    </div>
  );
}
