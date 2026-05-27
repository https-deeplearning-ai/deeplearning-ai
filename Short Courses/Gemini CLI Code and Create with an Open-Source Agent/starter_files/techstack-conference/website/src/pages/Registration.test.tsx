import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { Registration } from './Registration';

// Mock useNavigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe('Registration Page', () => {
  beforeEach(() => {
    mockNavigate.mockClear();
  });

  it('completes the registration flow', async () => {
    render(
      <MemoryRouter>
        <Registration />
      </MemoryRouter>
    );

    // Step 1: Selection
    expect(screen.getByText('Registration Packages')).toBeInTheDocument();
    
    // Select "Innovator" pass (it has "Select Pass" button)
    const selectButtons = screen.getAllByText('Select Pass');
    fireEvent.click(selectButtons[1]); // Innovator is the second one

    // Step 2: Form
    await waitFor(() => {
      expect(screen.getByText('Complete Registration')).toBeInTheDocument();
    });
    expect(screen.getByText(/Innovator Pass/)).toBeInTheDocument();

    // Fill form
    fireEvent.change(screen.getByPlaceholderText('Jane'), { target: { value: 'Alice' } });
    fireEvent.change(screen.getByPlaceholderText('Doe'), { target: { value: 'Smith' } });
    fireEvent.change(screen.getByPlaceholderText('jane@company.com'), { target: { value: 'alice@example.com' } });
    fireEvent.change(screen.getByPlaceholderText('Acme Inc.'), { target: { value: 'Wonderland' } });
    fireEvent.change(screen.getByPlaceholderText('Software Engineer'), { target: { value: 'Explorer' } });

    // Submit
    const submitBtn = screen.getByText('Complete Payment');
    fireEvent.click(submitBtn);

    // Check loading state
    expect(screen.getByText('Processing...')).toBeInTheDocument();

    // Step 3: Success
    // Wait for the 1500ms timeout in the component
    await waitFor(() => {
      expect(screen.getByText("You're all set!")).toBeInTheDocument();
    }, { timeout: 3000 });

    expect(screen.getByText(/Alice Smith/)).toBeInTheDocument();
    expect(screen.getByText('alice@example.com')).toBeInTheDocument();
  });
});
