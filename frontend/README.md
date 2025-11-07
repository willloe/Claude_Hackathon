# AI TA Platform - Frontend

React-based web interface for the AI Teaching Assistant platform.

## Features

- **Modern React** with hooks and context
- **Responsive Design** with Tailwind CSS
- **Role-Based UI** for instructors and students
- **Real-time Chat** interface for Q&A
- **Material Management** with drag-and-drop uploads
- **Analytics Dashboard** for instructors
- **Citation Display** with expandable source snippets

## Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Run Development Server

```bash
npm run dev
```

Application will start at: **http://localhost:5173**

### 3. Build for Production

```bash
npm run build
```

Output will be in `dist/` directory.

## Project Structure

```
frontend/
├── src/
│   ├── pages/                    # Route components
│   │   ├── Login.jsx            # Login page
│   │   ├── Register.jsx         # Registration page
│   │   ├── InstructorDashboard.jsx  # Instructor course list
│   │   ├── CourseDetail.jsx     # Course management (instructor)
│   │   ├── StudentCourses.jsx   # Course browser (student)
│   │   └── ChatInterface.jsx    # Q&A chat (student)
│   ├── components/               # Reusable components
│   │   ├── Navbar.jsx           # Navigation bar
│   │   ├── ProtectedRoute.jsx   # Auth wrapper
│   │   ├── LoadingSpinner.jsx   # Loading indicator
│   │   └── CitationBadge.jsx    # Source citation display
│   ├── context/
│   │   └── AuthContext.jsx      # Global auth state
│   ├── api/
│   │   └── client.js            # Axios API client
│   ├── App.jsx                  # Main app with routing
│   ├── main.jsx                 # Entry point
│   └── index.css                # Global styles
├── index.html
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
├── package.json
└── README.md
```

## Routes

### Public Routes
- `/login` - User login
- `/register` - User registration

### Instructor Routes
- `/instructor` - Dashboard (course list)
- `/instructor/course/:id` - Course detail page
  - Materials tab: Upload/manage PDFs
  - Policies tab: Configure AI behavior
  - Simulator tab: Test AI responses
  - Analytics tab: View usage stats

### Student Routes
- `/student` - Course browser
- `/student/chat/:id` - Q&A chat interface

### Default Route
- `/` - Redirects based on role

## Components

### AuthContext
Global authentication state management.

```jsx
import { useAuth } from './context/AuthContext';

function MyComponent() {
  const { user, login, logout, isInstructor } = useAuth();

  // Use auth state and methods
}
```

### ProtectedRoute
Wrapper for authenticated routes.

```jsx
<ProtectedRoute requireInstructor>
  <InstructorDashboard />
</ProtectedRoute>
```

### CitationBadge
Displays source references with expandable snippets.

```jsx
<CitationBadge
  source={{
    filename: "lecture1.pdf",
    page: 5,
    chunk_text: "..."
  }}
  index={0}
/>
```

## API Client

The API client (`src/api/client.js`) provides:

- **Automatic token injection** from localStorage
- **Error handling** with 401 redirect
- **Type-safe API methods**

```javascript
import { coursesAPI, qaAPI } from './api/client';

// List courses
const courses = await coursesAPI.list();

// Ask question
const answer = await qaAPI.ask(courseId, "What is RAG?");
```

### Available API Methods

```javascript
// Auth
authAPI.register(data)
authAPI.login(data)
authAPI.getMe()

// Courses
coursesAPI.create(data)
coursesAPI.list()
coursesAPI.get(id)
coursesAPI.update(id, data)
coursesAPI.delete(id)

// Materials
materialsAPI.upload(courseId, formData)
materialsAPI.list(courseId)
materialsAPI.delete(materialId)

// Policies
policiesAPI.update(courseId, data)
policiesAPI.get(courseId)

// Q&A
qaAPI.ask(courseId, question)
qaAPI.getLogs(courseId)

// Analytics
analyticsAPI.get(courseId)
```

## Styling

Using **Tailwind CSS** utility-first framework.

### Custom Scrollbar
Defined in `index.css` for better aesthetics.

### Color Scheme
- Primary: Blue (600, 700)
- Success: Green (100, 700)
- Error: Red (50, 600)
- Gray scale for backgrounds and text

### Responsive Breakpoints
- `sm`: 640px
- `md`: 768px
- `lg`: 1024px

## State Management

### Local State
- Component-level state with `useState`
- Effect hooks with `useEffect`

### Global State
- Auth context for user data
- Token stored in localStorage

### Form Handling
- Controlled components
- Validation on submit
- Error display

## User Flows

### Instructor Flow

1. **Login/Register** as instructor
2. **Create Course** from dashboard
3. **Upload PDFs** in course detail
4. **Configure Policies** (persona, rules)
5. **Test AI** with simulator
6. **View Analytics** and Q&A logs

### Student Flow

1. **Login/Register** as student
2. **Browse Courses** (published only)
3. **Select Course** and open chat
4. **Ask Questions** and get answers
5. **View Citations** for sources
6. **Continue Conversation** or start new

## Development Tips

### Hot Reload
Vite provides instant HMR (Hot Module Replacement).

### Debugging
- Use React DevTools browser extension
- Check network tab for API calls
- Console logs in components

### Code Organization
- Keep components small and focused
- Extract reusable logic to hooks
- Use meaningful variable names
- Add comments for complex logic

## Building for Production

```bash
# Build optimized bundle
npm run build

# Preview production build
npm run preview
```

### Deployment Options

**Vercel:**
```bash
vercel deploy
```

**Netlify:**
```bash
netlify deploy --prod
```

**Docker:**
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
RUN npm install -g serve
CMD ["serve", "-s", "dist", "-l", "3000"]
```

## Environment Variables

For production, configure:

- API base URL (if different from default)
- Enable production mode

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## Performance Optimization

- Code splitting with lazy loading
- Image optimization
- Minimize bundle size
- Use production build for deployment

## Accessibility

- Semantic HTML elements
- ARIA labels where needed
- Keyboard navigation support
- Color contrast compliance

## Common Issues

### Build fails
- Clear node_modules: `rm -rf node_modules && npm install`
- Update Node.js to 18+
- Check package.json for conflicts

### API calls fail
- Verify backend is running on port 8000
- Check CORS settings in backend
- Inspect network tab for errors

### Styles not applying
- Ensure Tailwind CSS is configured
- Check PostCSS config
- Verify class names are correct

### Auth not persisting
- Check localStorage is enabled
- Verify token is being saved
- Check browser security settings

## Scripts

```json
{
  "dev": "vite",              // Start dev server
  "build": "vite build",      // Build for production
  "preview": "vite preview"   // Preview production build
}
```

## Dependencies

### Core
- **react** (18.2.0) - UI library
- **react-dom** (18.2.0) - React DOM rendering
- **react-router-dom** (6.21.0) - Routing
- **axios** (1.6.5) - HTTP client

### Dev Dependencies
- **vite** (5.0.11) - Build tool
- **@vitejs/plugin-react** (4.2.1) - React plugin
- **tailwindcss** (3.4.1) - CSS framework
- **autoprefixer** (10.4.16) - CSS vendor prefixes
- **postcss** (8.4.33) - CSS processing

## Further Improvements

- Add TypeScript for type safety
- Implement React Query for caching
- Add error boundaries
- Implement lazy loading for routes
- Add unit tests with Vitest
- Add E2E tests with Playwright

---

For backend setup, see `backend/README.md`
