import type { Status } from './types';

export async function fetchStatus(): Promise<Status> {
  const response = await fetch(`status.json?ts=${Date.now()}`, { cache: 'no-store' });
  if (!response.ok) {
    throw new Error(`status.json returned ${response.status}`);
  }
  return response.json();
}
