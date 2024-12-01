import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import PlaylistCard from 'components/Cards/PlaylistCard/PlaylistCard';

const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

describe('PlaylistCard Component', () => {
  const refreshSidebarDataMock = jest.fn();

  it('should navigate to user page when artist button is clicked', () => {
    render(
      <BrowserRouter>
        <PlaylistCard
          name="Test Playlist"
          photo="https://example.com/photo.jpg"
          owner="Test Owner"
          refreshSidebarData={refreshSidebarDataMock}
          description={''}
        />
      </BrowserRouter>
    );

    const artistButton = screen.getByText('Test Owner');
    fireEvent.click(artistButton);

    expect(mockNavigate).toHaveBeenCalledWith('/user/Test Owner');
  });
});
