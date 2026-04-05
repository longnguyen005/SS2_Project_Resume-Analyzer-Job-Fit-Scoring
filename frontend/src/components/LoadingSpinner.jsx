import { Loader2 } from "lucide-react";

export default function LoadingSpinner({
  label = "Loading...",
  inline = false,
  fullScreen = false,
  size = 20,
  className = "",
}) {
  const classes = ["loading-spinner"];

  if (inline) {
    classes.push("inline");
  }

  if (fullScreen) {
    classes.push("fullscreen");
  }

  if (className) {
    classes.push(className);
  }

  return (
    <div className={classes.join(" ")}>
      <Loader2 className="spinner-icon" size={size} aria-hidden="true" />
      {label ? <span>{label}</span> : null}
    </div>
  );
}
