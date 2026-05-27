import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { SessionDetail } from './SessionDetail';

const { mockSession } = vi.hoisted(() => {
  return {
    mockSession: {
      id: 'session-123',
      title: 'Test Session Title',
      description: 'Test Description',
      speaker: 'Jane Doe',
      category: 'Keynote',
      day: 'Day 1',
      time: '10:00 AM',
      location: 'Room 101',
      details: {
        fullDescription: 'Full Test Description',
        speakerBio: 'Expert in Testing',
        level: 'Advanced',
        tracks: ['Testing', 'Quality'],
        takeaways: ['Unit Testing', 'Integration Testing']
      }
    }
  };
});

vi.mock('../data/sessions', () => ({
  SESSIONS: [mockSession]
}));

const mockNavigate = vi.fn();

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe('SessionDetail', () => {
  beforeEach(() => {
    mockNavigate.mockClear();
  });

  it('renders session details when session is found', () => {
    render(
      <MemoryRouter initialEntries={['/catalog/session-123']}>
        <Routes>
          <Route path="/catalog/:sessionId" element={<SessionDetail />} />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText('Test Session Title')).toBeInTheDocument();
    expect(screen.getByText('Jane Doe')).toBeInTheDocument();
    expect(screen.getByText('Full Test Description')).toBeInTheDocument();
    expect(screen.getByText('Advanced')).toBeInTheDocument();
    expect(screen.getByText('Testing')).toBeInTheDocument();
  });

  it('renders "Session not found" when ID is invalid', () => {
    render(
      <MemoryRouter initialEntries={['/catalog/invalid-id']}>
        <Routes>
          <Route path="/catalog/:sessionId" element={<SessionDetail />} />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText('Session not found')).toBeInTheDocument();
  });

  it('navigates back when back button is clicked (main view)', () => {
    render(
      <MemoryRouter initialEntries={['/catalog/session-123']}>
        <Routes>
          <Route path="/catalog/:sessionId" element={<SessionDetail />} />
        </Routes>
      </MemoryRouter>
    );

    const backButton = screen.getByText('Back');
    fireEvent.click(backButton);
    expect(mockNavigate).toHaveBeenCalledWith(-1);
  });

  it('navigates back to catalog when back button is clicked (not found view)', () => {
    render(
      <MemoryRouter initialEntries={['/catalog/invalid-id']}>
        <Routes>
          <Route path="/catalog/:sessionId" element={<SessionDetail />} />
        </Routes>
      </MemoryRouter>
    );

    const backButton = screen.getByText('Back to Catalog');
    fireEvent.click(backButton);
    expect(mockNavigate).toHaveBeenCalledWith('/catalog');
  });
});
