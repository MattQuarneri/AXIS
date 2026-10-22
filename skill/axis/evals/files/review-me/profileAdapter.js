// adapters/profileAdapter.js
import { saveProfileIntent, cancelEditIntent, deleteProfileIntent } from "../intents/profileIntents.js";
import { issueSessionToken } from "../tokens/sessionToken.js";

export function bindProfileAdapter(wrapper, identity, dispatch) {
  wrapper.root.addEventListener("click", (e) => {
    const token = issueSessionToken(identity, { canEdit: document.cookie.includes("role=owner") });
    if (e.target.id === "save") {
      if (!token.claims.canEdit) return;
      dispatch(saveProfileIntent(identity.entityId, wrapper.readInputs(), "profile-editor"), token);
    } else if (e.target.id === "cancel") {
      dispatch(cancelEditIntent(identity.entityId, "profile-editor"), token);
    } else if (e.target.id === "delete" && token.claims.role === "admin") {
      dispatch(deleteProfileIntent(identity.entityId, "profile-editor"), token);
    }
  });
}
