import { useState } from 'react';

const DOMAINS = {
  google: 'google.com', microsoft: 'microsoft.com', amazon: 'amazon.com', zoho: 'zoho.com',
  swiggy: 'swiggy.com', tcs: 'tcs.com', accenture: 'accenture.com', atlassian: 'atlassian.com',
  netflix: 'netflix.com', spotify: 'spotify.com', twitch: 'twitch.tv', coinbase: 'coinbase.com',
  robinhood: 'robinhood.com', airbnb: 'airbnb.com', discord: 'discord.com', figma: 'figma.com',
  notion: 'notion.com', stripe: 'stripe.com', cloudflare: 'cloudflare.com', databricks: 'databricks.com',
  plaid: 'plaid.com', ramp: 'ramp.com',
};

export default function CompanyLogo({ company, size = 'md' }) {
  const [failed, setFailed] = useState(false);
  const key = (company?.name || '').toLowerCase().replace(/[^a-z0-9]/g, '');
  const domain = Object.entries(DOMAINS).find(([name]) => key.includes(name))?.[1];
  const fallbackLogo = domain ? `https://www.google.com/s2/favicons?domain=${domain}&sz=128` : null;
  const logo = company?.logo_url || fallbackLogo;
  const initials = (company?.name || '?').split(/\s+/).filter(Boolean).slice(0, 2).map((part) => part[0]).join('').toUpperCase();

  return <div className={`company-logo company-logo-${size}`} title={company?.name}>{logo && !failed ? <img src={logo} alt={`${company.name} logo`} onError={() => setFailed(true)} /> : <span>{initials}</span>}</div>;
}
