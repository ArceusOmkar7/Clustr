# Clustr Frontend

A modern, responsive web application for the Clustr project built with React, TypeScript, and Tailwind CSS.

## Features

- **Drag-and-Drop File Upload**: Intuitive interface for uploading multiple images at once
- **Real-time Upload Progress**: Visual feedback during file uploads with progress bars
- **Image Preview**: Preview images before and after upload
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Dark/Light Theme Support**: Automatic theme detection with manual toggle option
- **Toast Notifications**: User-friendly notifications for upload success and errors

## Tech Stack

- **React 19**: Modern UI library for building interactive user interfaces
- **TypeScript**: Static typing for improved code quality and developer experience
- **Vite**: Fast build tool and development server
- **TailwindCSS**: Utility-first CSS framework for rapid UI development
- **Axios**: HTTP client for API requests with upload progress support
- **React Dropzone**: Drag-and-drop file upload component
- **Radix UI**: Accessible UI primitives for building robust components
- **Lucide React**: Beautiful, consistent icon set
- **Sonner**: Elegant toast notifications
- **React Router**: Client-side routing between application pages

## Project Structure

```
frontend/
├── public/                  # Static assets
├── src/
│   ├── assets/              # Local images, icons, etc.
│   │   └── *.tsx            # Feature-specific components
│   ├── hooks/               # Custom React hooks
│   ├── lib/                 # Utility functions and configurations
│   ├── pages/               # Application page components
│   ├── services/            # API service modules
│   ├── types/               # TypeScript types and interfaces
│   ├── App.tsx              # Main application component
│   └── main.tsx             # Application entry point
├── index.html               # HTML template
├── package.json             # Project dependencies and scripts
├── tsconfig.json            # TypeScript configuration
└── vite.config.ts           # Vite configuration
```

## Key Components

- **UploadComponent**: Main file upload interface with drag-and-drop functionality
- **ThemeProvider**: Handles light/dark theme switching and persistence
- **Navbar**: Application navigation and theme toggle

## Getting Started

### Prerequisites

- Node.js v14 or higher
- npm or yarn

### Installation

```bash
# Install dependencies
npm install
```

### Development

```bash
# Start the development server
npm run dev
```

This will start the development server at http://localhost:5173

### Building for Production

```bash
# Type check and build the application
npm run build

# Preview the production build locally
npm run preview
```

## Configuration

The application uses environment variables for configuration. Create a `.env` file in the root directory with the following variables:

```
# API configuration
VITE_API_BASE_URL=http://localhost:5000
```

## API Integration

The application communicates with the Clustr backend API for file uploads and retrieval:

- File uploads are sent to the `/api/upload` endpoint
- Upload progress is tracked in real-time
- Server responses include file metadata and preview URLs