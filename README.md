# Name Uniqueness Dashboard

A web dashboard for analyzing and comparing the uniqueness of names based on frequency, structural characteristics, and letter distribution.

## Features

- Calculate uniqueness scores for first names, last names, or full names
- Compare multiple names and rank them by uniqueness
- Interactive charts and visualizations
- Modern UI with responsive design

## Tech Stack

- **Backend**: Python with Flask API
- **Frontend**: React with TypeScript and Tailwind CSS
- **Deployment**: Vercel

## Project Structure

```
├── api/                  # Python API endpoints
│   ├── index.py          # Main API file
│   └── requirements.txt  # Python dependencies
├── frontend/             # React frontend
│   ├── public/           # Static files
│   ├── src/              # React components and logic
│   ├── package.json      # Frontend dependencies
│   ├── tsconfig.json     # TypeScript configuration
│   ├── tailwind.config.js # Tailwind CSS configuration
│   └── postcss.config.js # PostCSS configuration
├── name_data/            # Name frequency data
├── NameUniquenessScorer.py # Core name scoring functionality
├── vercel.json           # Vercel deployment configuration
└── README.md             # Project documentation
```

## Local Development

1. Install backend dependencies:

   ```
   pip install -r api/requirements.txt
   ```

2. Install frontend dependencies:

   ```
   cd frontend
   npm install
   ```

3. Run the backend API:

   ```
   cd api
   python index.py
   ```

4. Run the frontend development server:

   ```
   cd frontend
   npm start
   ```

5. Open [http://localhost:3000](http://localhost:3000) in your browser

## Deployment to Vercel

1. Install the Vercel CLI:

   ```
   npm install -g vercel
   ```

2. Login to Vercel:

   ```
   vercel login
   ```

3. Deploy the project:

   ```
   vercel
   ```

4. For production deployment:
   ```
   vercel --prod
   ```

## Environment Variables

No environment variables are required for basic functionality.

## License

This project is based on the Name Uniqueness Score Tool.
