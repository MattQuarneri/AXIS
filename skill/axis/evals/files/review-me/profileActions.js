// actions/profileActions.js
import { UserProfileForm } from "../forms/userProfile.js";

export async function loadProfile(state, intent) {
  const res = await fetch(`/api/users/${intent.identityRef}/profile`);
  const data = await res.json();
  return { delta: { ...data, _loading: false }, effects: [] };
}

export function saveProfile(state, intent) {
  const next = { ...state, ...intent.payload, updatedAt: Date.now() };
  const violations = UserProfileForm.invariants.map((inv) => inv(next)).filter((r) => r !== true);
  if (violations.length > 0) throw new Error(violations.join(", "));
  return {
    delta: next,
    effects: [{
      kind: "HTTP_PUT",
      target: `/api/users/${intent.identityRef}/profile`,
      payload: intent.payload,
      execute: async () => fetch(`/api/users/${intent.identityRef}/profile`, { method: "PUT", body: JSON.stringify(intent.payload) }),
    }],
  };
}

export function cancelEdit(state, intent) {
  return { delta: { _resetToCommitted: true }, effects: [] };
}
