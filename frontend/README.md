# Educational AI Agent - Frontend

React-based frontend for the Educational AI Agent system.

## Technology Stack

- **React 18** - UI library with hooks
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first styling
- **Lucide React** - Icon library
- **Axios** - HTTP client (optional)

## Project Structure

```
frontend/
├── public/
│   ├── index.html          # HTML template
│   ├── manifest.json       # PWA manifest
│   └── favicon.ico         # App icon
├── src/
│   ├── App.tsx             # Main application component
│   ├── App.css             # App-specific styles
│   ├── index.tsx           # React entry point
│   ├── index.css           # Global styles + Tailwind
│   ├── components/         # Reusable components (future)
│   ├── services/           # API services (future)
│   └── types/              # TypeScript types (future)
├── .env.example            # Environment variables template
├── package.json            # Dependencies
├── tsconfig.json           # TypeScript config
├── tailwind.config.js      # Tailwind config
├── Dockerfile              # Container build
└── nginx.conf              # Production server config
```

## Setup

### Prerequisites
- Node.js 18+
- npm 9+

### Installation

1. **Install dependencies**
```bash
npm install
```

2. **Set up environment**
```bash
cp .env.example .env
# Edit .env with your backend URL
```

3. **Run development server**
```bash
npm start
```

The app will open at http://localhost:3000

## Environment Variables

Create a `.env` file:

```env
# Backend API URL
REACT_APP_API_URL=http://localhost:8000

# WebSocket URL (for real-time features)
REACT_APP_WS_URL=ws://localhost:8000

# Enable WebSocket (set to 'true' to use WebSocket instead of REST)
REACT_APP_USE_WEBSOCKET=false

# Environment
REACT_APP_ENVIRONMENT=development
```

## Features

### Current Implementation

1. **Chat Interface**
   - Real-time messaging with AI agent
   - Message history
   - Typing indicators
   - Auto-scroll to latest message

2. **Student Profile**
   - Learning level (Beginner/Intermediate/Advanced/Expert)
   - Progress tracking (0-100%)
   - Topics learned display

3. **Session Analytics**
   - Questions asked counter
   - Topics explored counter
   - Session time tracker

4. **Quick Topics**
   - Pre-defined question prompts
   - Easy topic exploration

### Communication Modes

**REST API Mode (Default)**
- Uses HTTP POST requests
- More reliable for unstable connections
- Works everywhere
- Set `REACT_APP_USE_WEBSOCKET=false`

**WebSocket Mode (Optional)**
- Real-time bidirectional communication
- Lower latency
- Better for live updates
- Set `REACT_APP_USE_WEBSOCKET=true`

## Available Scripts

### `npm start`
Runs the app in development mode at http://localhost:3000

### `npm test`
Launches the test runner in interactive watch mode

### `npm run build`
Builds the app for production to the `build` folder

### `npm run lint`
Runs ESLint to check code quality

### `npm run format`
Formats code with Prettier

## API Integration

The frontend communicates with the backend API:

### REST Endpoints Used

```typescript
// Send message to agent
POST /api/message
Body: {
  student_id: string,
  message: string,
  allow_web_search: boolean
}
Response: {
  message: string,
  student_level: string,
  progress: number,
  topics_detected: string[],
  tools_used: string[]
}

// Get student profile
GET /api/student/{student_id}/profile
Response: {
  student_id: string,
  level: string,
  progress: number,
  topics: string[]
}
```

### WebSocket Events

```typescript
// Connect
ws://localhost:8000/ws/chat/{student_id}

// Send message
{
  message: string,
  allow_web_search: boolean
}

// Receive message
{
  type: 'message',
  data: {
    message: string,
    topics_detected: string[]
  }
}

// Receive progress update
{
  type: 'progress',
  data: {
    progress: number,
    level: string,
    topics: string[]
  }
}
```

## Building for Production

### Local Build

```bash
npm run build
```

Creates optimized production build in `build/` folder.

### Docker Build

```bash
docker build -t eduai-frontend .
docker run -p 80:80 eduai-frontend
```

### Environment-Specific Builds

**Production**
```bash
REACT_APP_API_URL=https://api.yourdomain.com npm run build
```

**Staging**
```bash
REACT_APP_API_URL=https://staging-api.yourdomain.com npm run build
```

## Deployment

### Static Hosting (Netlify, Vercel)

1. Build the app: `npm run build`
2. Deploy the `build/` folder
3. Set environment variables in hosting platform
4. Configure redirects for React Router

**Netlify `_redirects` file:**
```
/*    /index.html   200
```

**Vercel `vercel.json`:**
```json
{
  "rewrites": [{ "source": "/(.*)", "destination": "/" }]
}
```

### Docker Deployment

See main README.md and DEPLOYMENT.md for full instructions.

## Customization

### Styling

The app uses Tailwind CSS. Customize in `tailwind.config.js`:

```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: '#4f46e5',  // Indigo
        secondary: '#10b981', // Green
      }
    }
  }
}
```

### Adding Components

Create new components in `src/components/`:

```typescript
// src/components/ProgressChart.tsx
import React from 'react';

interface Props {
  progress: number;
}

export const ProgressChart: React.FC<Props> = ({ progress }) => {
  return (
    <div className="progress-chart">
      {/* Your component */}
    </div>
  );
};
```

Import and use in App.tsx:
```typescript
import { ProgressChart } from './components/ProgressChart';
```

## Performance Optimization

### Current Optimizations

1. **React.memo** for expensive components
2. **useCallback** for event handlers
3. **Code splitting** with lazy loading
4. **Image optimization**
5. **Bundle size optimization**

### Lighthouse Scores Target

- Performance: 90+
- Accessibility: 100
- Best Practices: 100
- SEO: 100

## Accessibility

The app follows WCAG 2.1 AA standards:

- ✅ Keyboard navigation
- ✅ ARIA labels
- ✅ Color contrast
- ✅ Screen reader support
- ✅ Focus indicators
- ✅ Semantic HTML

## Browser Support

- Chrome (last 2 versions)
- Firefox (last 2 versions)
- Safari (last 2 versions)
- Edge (last 2 versions)
- Mobile browsers (iOS Safari, Chrome Android)

## Troubleshooting

### Port Already in Use

```bash
# Kill process on port 3000
npx kill-port 3000

# Or use different port
PORT=3001 npm start
```

### API Connection Issues

Check:
1. Backend is running at correct URL
2. CORS is enabled on backend
3. Environment variables are set correctly
4. Network firewall settings

### Build Errors

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

## Contributing

See main CONTRIBUTING.md for guidelines.

### Code Style

- Use TypeScript for all new files
- Follow React best practices
- Use functional components with hooks
- Add PropTypes or TypeScript interfaces
- Write meaningful commit messages

### Testing

```bash
# Run tests
npm test

# Run tests with coverage
npm test -- --coverage

# Update snapshots
npm test -- -u
```

## Future Enhancements

- [ ] Voice input/output
- [ ] Dark mode
- [ ] Offline mode (PWA)
- [ ] Multi-language support
- [ ] Mobile app (React Native)
- [ ] Advanced analytics dashboard
- [ ] Peer learning features
- [ ] Gamification elements

## License

MIT License - See LICENSE file in root directory

## Support

- Issues: https://github.com/yourusername/educational-ai-agent/issues
- Discussions: https://github.com/yourusername/educational-ai-agent/discussions
