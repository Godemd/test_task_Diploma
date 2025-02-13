import React from 'react';
import '@testing-library/jest-dom/extend-expect';
import { render, screen } from '@testing-library/react';
import { Provider } from 'react-redux';
import App from './App';
import store from './core/store';

const renderWithProvider = (component) =>
  render(<Provider store={store}>{component}</Provider>);

describe('Тесты компонента App', () => {
  test('отображается заголовок "Application"', async () => {
    renderWithProvider(<App />);
    const appHeader = await screen.findByText(/application/i);
    expect(appHeader).toBeInTheDocument();
  });

  test('отображается заголовок "Авторизация"', async () => {
    renderWithProvider(<App />);
    const authHeader = await screen.findByText(/авторизация/i);
    expect(authHeader).toBeInTheDocument();
  });

  test('отображается кнопка "Войти"', () => {
    renderWithProvider(<App />);
    const loginButton = screen.getByText(/войти/i);
    expect(loginButton).toBeInTheDocument();
  });
});
