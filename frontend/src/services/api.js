import axios from 'axios';

const API_URL = 'http://localhost:8000';

export async function loginUser({ username, password }) {
  const params = new URLSearchParams();
  params.append('username', username);
  params.append('password', password);
  const response = await axios.post(`${API_URL}/login`, params, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });
  return response.data
}

export async function fetchCharacters(token) {
    const response = await axios.get(`${API_URL}/characters`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  }

export async function fetchCharacterById(id, token) {
  const response = await axios.get(`${API_URL}/characters/${id}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return response.data;
}