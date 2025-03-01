# Name Uniqueness Dashboard - Vercel Deployment

This project provides a serverless backend for the Name Uniqueness Dashboard using Vercel's serverless functions.

## Project Structure

- `api/index.py`: The main serverless function that handles API requests
- `api/requirements.txt`: Dependencies for the serverless function
- `vercel.json`: Configuration for Vercel deployment
- `name_data/`: Directory containing name frequency data
- `name_uniqueness_scorer.py`: The core name scoring logic

## API Endpoints

The API provides the following endpoints:

- `GET /api`: Health check endpoint
- `POST /api/score-name`: Score a single name's uniqueness
- `POST /api/compare-names`: Compare the uniqueness of multiple names

### Score Name Endpoint

**Request:**

```json
{
  "firstName": "John",
  "lastName": "Smith"
}
```

**Response:**

```json
{
  "score": 42,
  "type": "full",
  "fullName": "John Smith",
  "firstName": "John",
  "lastName": "Smith"
}
```

### Compare Names Endpoint

**Request:**

```json
{
  "names": [
    ["John", "Smith"],
    ["Luna", "Zhang"],
    ["Zephyr", ""]
  ]
}
```

**Response:**

```json
{
  "results": [
    {
      "name": "John Smith",
      "score": 42
    },
    {
      "name": "Luna Zhang",
      "score": 78
    },
    {
      "name": "Zephyr",
      "score": 95
    }
  ]
}
```

## Deployment Instructions

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

## Frontend Configuration

After deploying the backend, update the frontend's API base URL in `frontend/src/App.tsx`:

```typescript
const api = axios.create({
  baseURL: "https://your-vercel-deployment-url.vercel.app/api",
});
```

## Notes

- The serverless function has a 10-second execution limit
- The function is allocated 1GB of memory to handle the name data processing
- All name data files are included in the deployment
