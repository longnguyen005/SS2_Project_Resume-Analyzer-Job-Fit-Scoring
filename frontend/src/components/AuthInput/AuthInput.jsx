import "./AuthInput.css";

export default function AuthInput({ label, type = "text", value, onChange, placeholder, helper }) {
  return (
    <label className="auth-field">
      <span>{label}</span>
      <input type={type} value={value} onChange={onChange} placeholder={placeholder} />
      {helper ? <small>{helper}</small> : null}
    </label>
  );
}
