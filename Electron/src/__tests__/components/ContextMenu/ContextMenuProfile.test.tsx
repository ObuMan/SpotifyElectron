import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom'; 
import { useNavigate } from 'react-router-dom';
import ContextMenuProfile from 'components/AdvancedUIComponents/ContextMenu/Profile/ContextMenuProfile';


jest.mock('react-router-dom', () => ({
  useNavigate: jest.fn(),
}));

jest.mock('utils/token', () => ({
  getTokenRole: jest.fn(),
  getTokenUsername: jest.fn(),
}));

describe('ContextMenuProfile Component', () => {
  const mockHandleLogout = jest.fn();
  const mockHandleClose = jest.fn();
  const mockNavigate = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    (useNavigate as jest.Mock).mockReturnValue(mockNavigate);
  });

  it('should render the component correctly', () => {
    render(
      <ContextMenuProfile
        handleLogout={mockHandleLogout}
        handleClose={mockHandleClose}
      />
    );

    expect(screen.getByText('Perfil')).toBeInTheDocument();
    expect(screen.getByText('Cerrar sesión')).toBeInTheDocument();
  });

  it('should call handleClickProfile and navigate correctly', () => {
    const username = 'testUser';
    const role = 'user';
    const { getTokenRole, getTokenUsername } = jest.requireMock('utils/token');
    getTokenRole.mockReturnValue(role);
    getTokenUsername.mockReturnValue(username);

    render(
      <ContextMenuProfile
        handleLogout={mockHandleLogout}
        handleClose={mockHandleClose}
      />
    );

    const profileButton = screen.getByText('Perfil');
    fireEvent.click(profileButton);

    expect(mockNavigate).toHaveBeenCalledWith(`/${role}/${username}`);
    expect(mockHandleClose).toHaveBeenCalled();
  });

  it('should call handleClickLogout correctly', () => {
    render(
      <ContextMenuProfile
        handleLogout={mockHandleLogout}
        handleClose={mockHandleClose}
      />
    );

    const logoutButton = screen.getByText('Cerrar sesión');
    fireEvent.click(logoutButton);

    expect(mockHandleLogout).toHaveBeenCalledWith(false);
  });
});
