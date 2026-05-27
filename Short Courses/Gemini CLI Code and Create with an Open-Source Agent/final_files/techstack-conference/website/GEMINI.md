# TechStack Conference Website

## Project Overview
This is the official website for the **TechStack Conference**, a web application built with **React 19**, **TypeScript**, and **Vite**. The site provides information about the conference schedule, speakers, sessions, and registration. It features a modern, responsive design using **Tailwind CSS v4** and **Framer Motion** for animations.

## Tech Stack
*   **Framework:** React 19
*   **Build Tool:** Vite
*   **Language:** TypeScript
*   **Styling:** Tailwind CSS v4 (configured via `src/index.css` with CSS variables)
*   **Routing:** React Router Dom v7
*   **Animations:** Framer Motion
*   **Icons:** Lucide React
*   **Testing:** Vitest, React Testing Library
*   **Linting:** ESLint

## Getting Started

### Prerequisites
*   Node.js (Ensure a compatible version is installed)
*   npm

### Key Commands
*   **Install Dependencies:** `npm install`
*   **Start Development Server:** `npm run dev` (Starts Vite dev server)
*   **Build for Production:** `npm run build` (Runs TypeScript compiler and Vite build)
*   **Preview Production Build:** `npm run preview`
*   **Run Tests:** `npm run test` (Runs Vitest)
*   **Lint Code:** `npm run lint`

## Project Structure
*   `src/` - Source code root.
    *   `App.tsx` - Main application component handling routing and layout.
    *   `main.tsx` - Application entry point.
    *   `lazyLoad.ts` - Centralized lazy loading logic for pages.
    *   `components/` - Reusable UI components (e.g., `Layout`, `Loading`, `ParticleBackground`).
    *   `pages/` - Page-level components corresponding to routes (e.g., `Home`, `Catalog`, `SessionDetail`).
    *   `data/` - Static data files (e.g., `features.ts`, `sessions.ts`) acting as a mock database.
    *   `index.css` - Global styles and Tailwind CSS v4 configuration (theme variables).
*   `public/` - Static assets like `logo.svg`.
*   `schedule.md` - Reference document for the conference schedule (human-readable).

## Development Conventions

### Styling
*   **Tailwind CSS v4:** The project uses the latest Tailwind CSS. Configuration is handled directly in `src/index.css` using the `@theme` directive.
*   **Color Palette:** Custom CSS variables define the color palette (e.g., `--color-primary-500`, `--color-secondary-500`). Use these variables or their Tailwind utility classes.
*   **Dark Mode:** Supported via the `.dark` class strategy.

### Routing & Performance
*   **Lazy Loading:** All major route components are lazy-loaded in `src/App.tsx` using `React.lazy` and `Suspense` to improve initial load time.
*   **Centralized Loading:** `src/lazyLoad.ts` likely contains helper functions or delays to simulate network requests or smooth transitions.

### Data Management
*   **Static Data:** Content is primarily driven by static TypeScript files in `src/data/`. When adding new content (e.g., sessions, speakers), update these files.

### Testing
*   **Unit/Integration Tests:** Located alongside components (e.g., `Home.test.tsx`). Use `npm run test` to execute.


