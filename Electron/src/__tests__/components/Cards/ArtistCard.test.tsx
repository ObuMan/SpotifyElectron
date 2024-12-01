import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter, useNavigate } from 'react-router-dom';
import '@testing-library/jest-dom'; 
import ArtistCard from 'components/Cards/ArtistCard/ArtistCard';

// Mock react-router-dom's useNavigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: jest.fn(), // Mock useNavigate
}));

// Cast useNavigate to Jest mock
(useNavigate as jest.Mock).mockReturnValue(mockNavigate);

// Mock the default thumbnail image
jest.mock('../../../assets/imgs/DefaultThumbnailPlaylist.jpg', () => 'default-thumbnail.jpg');

describe('ArtistCard Component', () => {
  it('should render the ArtistCard with name and photo', () => {
    render(
      <BrowserRouter>
        <ArtistCard name="Test Artist" photo="https://example.com/photo.jpg" />
      </BrowserRouter>
    );

    expect(screen.getByText('Test Artist')).toBeInTheDocument();
    const img = screen.getByAltText('artist thumbnail');
    expect(img).toHaveAttribute('src', 'https://example.com/photo.jpg');
  });

  it('should use the default thumbnail if photo URL is empty', () => {
    render(
      <BrowserRouter>
        <ArtistCard name="Test Artist" photo="" />
      </BrowserRouter>
    );

    const img = screen.getByAltText('artist thumbnail');
    expect(img).toHaveAttribute('src', 'default-thumbnail.jpg');
  });

  it('should navigate to artist page on button click', () => {
    render(
      <BrowserRouter>
        <ArtistCard name="Test Artist" photo="https://example.com/photo.jpg" />
      </BrowserRouter>
    );

    const button = screen.getByText('Artista');
    fireEvent.click(button);

    expect(mockNavigate).toHaveBeenCalledWith('/artist/Test Artist');
  });
});
