# Vue 3 + TypeScript Frontend

This is the Vue 3 + TypeScript version of the Document Processing System, migrated from React + TypeScript.


## Tech Stack

- **Vue 3.5.13** - Progressive JavaScript framework
- **TypeScript 5.9.3** - Type safety
- **Vite 6.0.3** - Build tool and dev server
- **Tailwind CSS 3.4.1** - Utility-first CSS
- **Axios 1.13.2** - HTTP client
- **XLSX 0.18.5** - Excel export functionality

## Project Structure

```
frontend-vue/
├── src/
│   ├── components/          # Vue components
│   │   ├── FileUpload.vue
│   │   ├── ProcessingStatus.vue
│   │   ├── ResultsTable.vue
│   │   └── DownloadButton.vue
│   ├── services/            # API client (unchanged)
│   │   └── api.ts
│   ├── types/               # TypeScript types (unchanged)
│   │   └── document.ts
│   ├── utils/               # Utilities (unchanged)
│   │   └── downloadUtils.ts
│   ├── App.vue              # Main app component
│   ├── main.ts              # App entry point
│   ├── index.css            # Global styles
│   └── App.css              # Component styles
├── public/                  # Static assets
├── index.html               # HTML template
├── vite.config.ts           # Vite configuration
├── tsconfig.json            # TypeScript config
├── tailwind.config.js       # Tailwind config
└── package.json             # Dependencies

```

## Installation & Setup

1. **Install dependencies** (already done):
   ```bash
   cd frontend-vue
   npm install
   ```

2. **Run development server**:
   ```bash
   npm run dev
   ```
   Opens at `http://localhost:5173`

3. **Build for production**:
   ```bash
   npm run build
   ```
   Output in `dist/` directory

4. **Preview production build**:
   ```bash
   npm run preview
   ```


**React (before)**:
```tsx
export const Component: React.FC<Props> = ({ value }) => {
  const [count, setCount] = useState(0)
  
  return (
    <div onClick={() => setCount(count + 1)}>
      {value}
    </div>
  )
}
```

**Vue (after)**:
```vue
<script setup lang="ts">
interface Props { value: string }
defineProps<Props>()
const count = ref(0)
</script>

<template>
  <div @click="count++">
    {{ value }}
  </div>
</template>
```

## Backend Integration

The Vue app connects to the same backend API:
- **API Base URL**: `http://localhost:8000`
- **Proxy configured**: `/api/*` routes through Vite dev server
- **No backend changes required**: All API contracts remain identical

### API Service
The `services/api.ts` file is **unchanged** from React version. Axios works identically in Vue.

## Features

All features from the React app are preserved:

1. ✅ **Drag & Drop File Upload** - Native HTML5 implementation
2. ✅ **Multi-file PDF Processing** - Batch document processing
3. ✅ **Real-time Status Updates** - Upload, processing, completion states
4. ✅ **Results Table** - Expandable rows with detailed information
5. ✅ **Data Export** - Download as CSV or Excel (.xlsx)
6. ✅ **Error Handling** - Comprehensive error display
7. ✅ **Responsive Design** - Mobile-friendly with Tailwind CSS
8. ✅ **Type Safety** - Full TypeScript integration

## Running Both Apps in Parallel (for testing)

You can run both React and Vue versions simultaneously:

**React app** (port 5173):
```bash
cd frontend
npm run dev
```

**Vue app** (change port or stop React first):
```bash
cd frontend-vue
npm run dev
```

## Verification Checklist

Before decommissioning the React app, verify:

- [ ] File upload works (drag & drop + click)
- [ ] Multiple files can be selected
- [ ] Processing status updates correctly
- [ ] Results table displays all data
- [ ] Row expansion shows detailed information
- [ ] CSV export works
- [ ] Excel export works
- [ ] Error states display properly
- [ ] All Tailwind styles render correctly
- [ ] Backend API integration works
- [ ] TypeScript compiles without errors

## What Wasn't Changed

These files are **identical** to the React version:
- `src/services/api.ts` - API client
- `src/types/document.ts` - TypeScript interfaces
- `src/utils/downloadUtils.ts` - CSV/Excel export logic
- `src/index.css` - Global styles
- `tailwind.config.js` - Tailwind configuration
- `postcss.config.js` - PostCSS configuration

## Build Output

Production build creates optimized assets:
- **HTML**: ~0.5 KB
- **CSS**: ~17 KB (4 KB gzipped)
- **Main JS**: ~123 KB (47 KB gzipped)
- **XLSX JS**: ~430 KB (142 KB gzipped)

## Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Lint code with ESLint

## Next Steps

1. **Test Thoroughly**: Verify all functionality works as expected
2. **Deploy Vue App**: When satisfied, deploy the Vue version
3. **Update CI/CD**: Point build/deploy pipelines to `frontend-vue`
4. **Archive React App**: Keep `frontend/` as backup or remove once confident

## Rollback Plan

If you need to rollback:
1. The original React app is still in `frontend/` directory
2. All files are unchanged and can be used immediately
3. Simply switch your deployment to point to `frontend/` instead of `frontend-vue/`

## Support

If you encounter any issues:
1. Check browser console for errors
2. Verify backend is running on port 8000
3. Ensure all dependencies are installed
4. Compare behavior with React version in `frontend/`

---

**Migration completed successfully! 🎉**

The Vue 3 app is ready for testing and deployment.
