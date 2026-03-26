import "./Footer.css";
import BrandLogo from "../BrandLogo/BrandLogo";

const columns = [
  { title: "Product", items: ["Features", "Pricing", "Examples"] },
  { title: "Resources", items: ["Blog", "Help Center", "Contact"] },
  { title: "Company", items: ["About", "Privacy", "Terms"] },
];

export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="shell footer-grid">
        <div className="footer-brand">
          <BrandLogo />
          <p>AI-powered resume analysis to help you land your dream job.</p>
        </div>
        {columns.map((column) => (
          <div key={column.title} className="footer-column">
            <h4>{column.title}</h4>
            {column.items.map((item) => (
              <a key={item} href="/" onClick={(event) => event.preventDefault()}>
                {item}
              </a>
            ))}
          </div>
        ))}
      </div>
      <div className="shell footer-bottom">
        <span>Copyright 2026 ResumeAI. All rights reserved.</span>
      </div>
    </footer>
  );
}
