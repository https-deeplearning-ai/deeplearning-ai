import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { Home } from './Home';
import * as LazyLoadExports from '../lazyLoad';
import { FEATURES } from '../data/features';

// Mock the prefetch functions
vi.mock('../lazyLoad', () => ({
  loadCatalog: vi.fn(),
  loadSponsors: vi.fn(),
  loadWhyAttendDetail: vi.fn()
}));

describe('Home Page', () => {
  it('renders the hero section with correct text', () => {
    render(
      <MemoryRouter>
        <Home />
      </MemoryRouter>
    );

    expect(screen.getByText(/The Future of/i)).toBeInTheDocument();
    expect(screen.getByText(/Artificial Intelligence/i)).toBeInTheDocument();
    expect(screen.getByText(/November 20-22, 2026/i)).toBeInTheDocument();
  });

  it('renders stats section', () => {
    render(
      <MemoryRouter>
        <Home />
      </MemoryRouter>
    );
    expect(screen.getByText('5,000+')).toBeInTheDocument();
    expect(screen.getByText('Attendees')).toBeInTheDocument();
    expect(screen.getByText('120+')).toBeInTheDocument();
  });

  it('renders all feature cards', () => {
    render(
      <MemoryRouter>
        <Home />
      </MemoryRouter>
    );

    FEATURES.forEach(feature => {
      expect(screen.getByText(feature.title)).toBeInTheDocument();
      expect(screen.getByText(feature.description)).toBeInTheDocument();
    });
  });

  it('prefetches catalog on hover', () => {
    render(
      <MemoryRouter>
        <Home />
      </MemoryRouter>
    );

    const exploreLink = screen.getByText('Explore Sessions');
    fireEvent.mouseEnter(exploreLink);
    expect(LazyLoadExports.loadCatalog).toHaveBeenCalled();
  });

  it('prefetches sponsors on hover', () => {
    render(
      <MemoryRouter>
        <Home />
      </MemoryRouter>
    );

    const sponsorLink = screen.getByText('Become a Sponsor');
    fireEvent.mouseEnter(sponsorLink);
    expect(LazyLoadExports.loadSponsors).toHaveBeenCalled();
  });
});
