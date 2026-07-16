export function unwrapData(response) {
  const payload = response?.data;
  if (payload && typeof payload === 'object' && 'data' in payload) {
    return payload.data;
  }
  return payload;
}

export function unwrapList(response, key) {
  const data = unwrapData(response);
  if (Array.isArray(data)) return data;
  if (key && Array.isArray(data?.[key])) return data[key];
  return [];
}

export function getApiError(error, fallback = 'Something went wrong') {
  const detail = error?.response?.data?.detail;
  const message = error?.response?.data?.message;
  if (Array.isArray(detail)) return detail.map((item) => item.msg || item.detail || String(item)).join(', ');
  return detail || message || error?.message || fallback;
}