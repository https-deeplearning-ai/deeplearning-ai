import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { Catalog } from './Catalog';

const { mockSessions } = vi.hoisted(() => {
  return {
    mockSessions: [
      {
        id: '1',
        title: 'React Keynote',
        description: 'Deep dive into React',
        speaker: 'Dr. Sarah Chen',
        category: 'Keynote',
        day: 'Day 1',
        time: '10:00 AM',
        location: 'Hall A',
        details: {
          fullDescription: 'Full description here',
          tracks: ['Frontend'],
          level: 'Beginner'
        }
      },
      {
        id: '2',
        title: 'Vue Workshop',
        description: 'Hands-on with Vue',
        speaker: 'Marcus Rodriguez',
        category: 'Learning Lab',
        day: 'Day 2',
        time: '2:00 PM',
        location: 'Room 200',
        details: {
            fullDescription: 'Full description here',
            tracks: ['Frontend'],
            level: 'Intermediate'
        }
      },
      {
        id: '3',
        title: 'AI in 2026',
        description: 'Future of AI',
        speaker: 'Emily Watson',
        category: 'Breakout',
        day: 'Day 1',
        time: '11:00 AM',
        location: 'Hall B',
        details: {
            fullDescription: 'Full description here',
            tracks: ['AI/ML'],
            level: 'Advanced'
        }
      }
    ]
  };
});

vi.mock('../data/sessions', () => ({
  SESSIONS: mockSessions
}));

describe('Catalog Page', () => {
  it('renders all sessions initially', () => {
    render(
      <MemoryRouter>
        <Catalog />
      </MemoryRouter>
    );
    expect(screen.getByText('React Keynote')).toBeInTheDocument();
    expect(screen.getByText('Vue Workshop')).toBeInTheDocument();
    expect(screen.getByText('AI in 2026')).toBeInTheDocument();
    expect(screen.getByText('Showing 3 sessions')).toBeInTheDocument();
  });

  it('filters by search query (title)', async () => {
    render(
      <MemoryRouter>
        <Catalog />
      </MemoryRouter>
    );
    const searchInput = screen.getByPlaceholderText(/Search sessions/i);
    fireEvent.change(searchInput, { target: { value: 'React' } });

    expect(screen.getByText('React Keynote')).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.queryByText('Vue Workshop')).not.toBeInTheDocument();
    });
    expect(screen.getByText('Showing 1 sessions')).toBeInTheDocument();
  });

  it('filters by Day', async () => {
    render(
      <MemoryRouter>
        <Catalog />
      </MemoryRouter>
    );
    // Find the select for Day. We can identify it by its value 'All' and order or by label.
    // Since we added labels, we can use getByLabelText.
    const daySelect = screen.getByLabelText('Day');

    fireEvent.change(daySelect, { target: { value: 'Day 2' } });

    await waitFor(() => {
      expect(screen.queryByText('React Keynote')).not.toBeInTheDocument();
    });
    expect(screen.getByText('Vue Workshop')).toBeInTheDocument();
  });

  it('filters by Category', async () => {
    render(
      <MemoryRouter>
        <Catalog />
      </MemoryRouter>
    );
    const categorySelect = screen.getByLabelText('Category');

    fireEvent.change(categorySelect, { target: { value: 'Keynote' } });

    expect(screen.getByText('React Keynote')).toBeInTheDocument();
    await waitFor(() => {
        expect(screen.queryByText('Vue Workshop')).not.toBeInTheDocument();
    });
  });

  it('filters by Level', async () => {
    render(
        <MemoryRouter>
            <Catalog />
        </MemoryRouter>
    );
    const levelSelect = screen.getByLabelText('Level');
    fireEvent.change(levelSelect, { target: { value: 'Advanced' } });

    expect(screen.getByText('AI in 2026')).toBeInTheDocument();
    await waitFor(() => {
        expect(screen.queryByText('React Keynote')).not.toBeInTheDocument();
    });
  });

  it('filters by Track', async () => {
    render(
        <MemoryRouter>
            <Catalog />
        </MemoryRouter>
    );
    const trackSelect = screen.getByLabelText('Track');
    fireEvent.change(trackSelect, { target: { value: 'AI/ML' } });

    expect(screen.getByText('AI in 2026')).toBeInTheDocument();
    await waitFor(() => {
        expect(screen.queryByText('React Keynote')).not.toBeInTheDocument();
    });
  });

  it('filters by Speaker', async () => {
    render(
        <MemoryRouter>
            <Catalog />
        </MemoryRouter>
    );
    const speakerSelect = screen.getByLabelText('Speaker');
    fireEvent.change(speakerSelect, { target: { value: 'Dr. Sarah Chen' } });

    expect(screen.getByText('React Keynote')).toBeInTheDocument();
    await waitFor(() => {
        expect(screen.queryByText('Vue Workshop')).not.toBeInTheDocument();
    });
  });

  it('shows no results message when no matches', () => {
    render(
      <MemoryRouter>
        <Catalog />
      </MemoryRouter>
    );
    const searchInput = screen.getByPlaceholderText(/Search sessions/i);
    fireEvent.change(searchInput, { target: { value: 'NonExistentTerm' } });

    expect(screen.getByText('No sessions found')).toBeInTheDocument();
    expect(screen.getByText('Showing 0 sessions')).toBeInTheDocument();
  });
});