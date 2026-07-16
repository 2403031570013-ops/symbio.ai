import { useMemo, useState } from 'react';
import { ChevronDown, HelpCircle, PlayCircle, Search, X } from 'lucide-react';
import { useLocation, useNavigate } from 'react-router-dom';

const docs = [
  {
    id: 'dashboard', paths: ['/dashboard', '/'], category: 'Operations',
    en: { title: 'Dashboard and Create Listing', useful: 'Monitor revenue, CO2 avoided, landfill diversion, AI matches, transactions, and start a new listing.', steps: ['Open Dashboard after login.', 'Review KPI cards and recent transactions.', 'Click Create new listing to go to Listings.', 'Use Help for page-specific guidance.'], mistakes: ['Ignoring stale data after changing users.', 'Expecting Create new listing to submit a form directly. It opens the listing form.'], troubleshooting: ['Refresh the browser if KPIs look stale.', 'If Create new listing does not open Listings, check the route /listings.'], faqs: [['What does Create new listing do?', 'It navigates to the upload form where material details and files are submitted.'], ['Where do stats come from?', 'They use dashboard data and seeded demo metrics in local development.']], tips: ['Create listings before reviewing AI matches for better recommendations.'] },
    hi: { title: 'डैशबोर्ड और नई लिस्टिंग', useful: 'Revenue, CO2 बचत, landfill diversion, AI matches, transactions देखें और नई listing शुरू करें।', steps: ['Login के बाद Dashboard खोलें।', 'KPI cards और recent transactions देखें।', 'Create new listing क्लिक करके Listings page खोलें।', 'Page-specific help के लिए Help button दबाएँ।'], mistakes: ['User बदलने के बाद पुराना data देखकर confuse होना।', 'Create new listing को direct submit समझना। यह listing form खोलता है।'], troubleshooting: ['KPI stale लगे तो browser refresh करें।', 'Button काम न करे तो /listings route जांचें।'], faqs: [['Create new listing क्या करता है?', 'यह upload form खोलता है जहाँ material details और files submit होती हैं।'], ['Stats कहाँ से आते हैं?', 'Local development में dashboard और seeded demo metrics से।']], tips: ['AI matches देखने से पहले material listing बनाएं।'] }
  },
  {
    id: 'listings', paths: ['/listings'], category: 'Materials',
    en: { title: 'Material, Certificate, Photo, and Document Upload', useful: 'Upload waste material details, certificate files, photos, and supporting documents so the platform can match buyers and sellers.', steps: ['Open Listings.', 'Fill material name, physical state, composition, quantity, and frequency.', 'Choose a certificate file.', 'Optionally choose a material photo and supporting document.', 'Click Submit listing and confirm it appears in Saved listings.'], mistakes: ['Uploading without a certificate.', 'Using vague composition such as mixed waste.', 'Uploading non-image files in the photo field.'], troubleshooting: ['If upload fails, login again and retry.', 'Check that backend is running on port 8000.', 'For production file uploads, confirm object storage environment variables are configured.'], faqs: [['Are files uploaded?', 'Yes. Production uploads use secure object-storage URLs, and local development clearly reports when storage is not configured.'], ['Can I upload photos?', 'Yes, material photos show a preview before submit.']], tips: ['Use exact units and clear certificate names.'] },
    hi: { title: 'Material, Certificate, Photo और Document Upload', useful: 'Waste material details, certificate files, photos और supporting documents upload करें ताकि buyers और sellers match हो सकें।', steps: ['Listings खोलें।', 'Material name, physical state, composition, quantity और frequency भरें।', 'Certificate file चुनें।', 'Optional material photo और supporting document चुनें।', 'Submit listing क्लिक करें और Saved listings में देखें।'], mistakes: ['Certificate के बिना submit करना।', 'Composition vague लिखना जैसे mixed waste।', 'Photo field में non-image file डालना।'], troubleshooting: ['Upload fail हो तो फिर login करके retry करें।', 'Backend port 8000 पर चल रहा है यह जांचें।', 'Production uploads के लिए object storage environment variables configured होने चाहिए।'], faqs: [['क्या files upload होती हैं?', 'हाँ। Production uploads secure object-storage URLs use करते हैं, और local development storage missing होने पर साफ error देता है।'], ['क्या photos upload कर सकते हैं?', 'हाँ, submit से पहले photo preview दिखता है।']], tips: ['Exact units और clear certificate names use करें।'] }
  },
  {
    id: 'matches', paths: ['/matches'], category: 'Marketplace',
    en: { title: 'AI Matches and Contact Buyer', useful: 'Review Symbio Score, partner fit, distance, carbon savings, and start a buyer conversation.', steps: ['Open AI Matches.', 'Review each match card and score.', 'Click Contact buyer.', 'Edit the prepared message.', 'Click Send message to create a negotiation thread.'], mistakes: ['Contacting without reviewing composition.', 'Sending incomplete shipment details.'], troubleshooting: ['If the modal does not open, reload the page.', 'If a message is empty, type a short note before sending.'], faqs: [['Is this real messaging?', 'Yes. Messages are persisted through the backend and live updates use WebSockets when the server is available.'], ['What is Symbio Score?', 'A compatibility score based on fit, distance, and impact.']], tips: ['Prioritize scores above 85.'] },
    hi: { title: 'AI Matches और Contact Buyer', useful: 'Symbio Score, partner fit, distance, carbon savings देखें और buyer conversation शुरू करें।', steps: ['AI Matches खोलें।', 'हर match card और score देखें।', 'Contact buyer क्लिक करें।', 'Prepared message edit करें।', 'Send message दबाकर negotiation thread बनाएं।'], mistakes: ['Composition review किए बिना contact करना।', 'Shipment details incomplete भेजना।'], troubleshooting: ['Modal न खुले तो page reload करें।', 'Message empty हो तो short note लिखें।'], faqs: [['क्या यह real messaging है?', 'Current local workflow में in-app negotiation action बनता है।'], ['Symbio Score क्या है?', 'Fit, distance और impact पर आधारित compatibility score।']], tips: ['85 से ऊपर scores को पहले contact करें।'] }
  },
  {
    id: 'recommendations', paths: ['/ai-recommendations'], category: 'AI',
    en: { title: 'AI Recommendations', useful: 'Review smart suggestions for materials, pricing, and routes. Demo recommendations appear when live data is empty.', steps: ['Open AI Insights.', 'Read confidence score and expected savings.', 'Click Accept or Reject.', 'Use accepted ideas to plan marketplace action.'], mistakes: ['Ignoring confidence score.', 'Rejecting useful demo suggestions without reading details.'], troubleshooting: ['If live recommendations are empty, demo recommendations are shown automatically.', 'If status update fails, refresh and try again.'], faqs: [['Why do I see Demo?', 'It keeps the page useful even when the database has no recommendations.'], ['Are accepted demos saved?', 'Demo status changes are local UI actions.']], tips: ['Accept material recommendations before price changes.'] },
    hi: { title: 'AI Recommendations', useful: 'Materials, pricing और routes के smart suggestions देखें। Live data empty हो तो demo recommendations दिखती हैं।', steps: ['AI Insights खोलें।', 'Confidence score और expected savings पढ़ें।', 'Accept या Reject क्लिक करें।', 'Accepted ideas से marketplace action plan करें।'], mistakes: ['Confidence score ignore करना।', 'Details पढ़े बिना demo suggestions reject करना।'], troubleshooting: ['Live recommendations empty हों तो demo recommendations अपने आप दिखती हैं।', 'Status update fail हो तो refresh करके retry करें।'], faqs: [['Demo क्यों दिखता है?', 'Database empty होने पर भी page useful रखने के लिए।'], ['Accepted demos save होते हैं?', 'Demo status changes local UI actions हैं।']], tips: ['Price changes से पहले material recommendations accept करें।'] }
  },
  {
    id: 'reports', paths: ['/esg', '/esg-dashboard', '/supply-chain', '/compliance', '/transactions'], category: 'Reports',
    en: { title: 'Reports, Exports, Supply Chain, and Compliance', useful: 'Use ESG reports, CSV/PDF exports, supply chain tracking, compliance checks, and transactions.', steps: ['Open ESG for analytics.', 'Click Export CSV to download spreadsheet data.', 'Click Export PDF to open a printable report.', 'Open Supply Chain to review inventory and shipments.', 'Open Compliance before high-value deals.'], mistakes: ['Blocking popups for PDF export.', 'Expecting CSV to include data outside the current dashboard.', 'Opening admin-only pages with non-admin role.'], troubleshooting: ['Allow popups for PDF print window.', 'If Supply Chain is empty, check seeded factory data.', 'If API returns 401, login again.'], faqs: [['Does Export PDF download directly?', 'It opens a report window so you can Save as PDF from print.'], ['Why was Supply Chain blank?', 'It was fixed by reading the shipments array correctly.']], tips: ['Export reports after refreshing dashboard data.'] },
    hi: { title: 'Reports, Exports, Supply Chain और Compliance', useful: 'ESG reports, CSV/PDF exports, supply chain tracking, compliance checks और transactions use करें।', steps: ['Analytics के लिए ESG खोलें।', 'Spreadsheet data download करने के लिए Export CSV क्लिक करें।', 'Printable report खोलने के लिए Export PDF क्लिक करें।', 'Inventory और shipments के लिए Supply Chain खोलें।', 'High-value deals से पहले Compliance खोलें।'], mistakes: ['PDF export popup block करना।', 'CSV में current dashboard से बाहर का data expect करना।', 'Non-admin role से admin pages खोलना।'], troubleshooting: ['PDF print window के लिए popups allow करें।', 'Supply Chain empty हो तो seeded factory data जांचें।', '401 आए तो फिर login करें।'], faqs: [['क्या Export PDF direct download करता है?', 'यह report window खोलता है जहाँ print से Save as PDF कर सकते हैं।'], ['Supply Chain blank क्यों था?', 'Shipments array सही read करके fix किया गया।']], tips: ['Reports export करने से पहले dashboard refresh करें।'] }
  },
  {
    id: 'email-verification', paths: ['/verify-email'], category: 'Account Security',
    en: { title: 'Email OTP Verification', useful: 'Verify a newly registered email with the six-digit one-time password delivered by SymbioAI through Resend.', steps: ['Open Verify Email after registration.', 'Confirm the email address.', 'Click Send verification code.', 'Check your inbox for the six-digit OTP.', 'Enter the code within five minutes and select Verify email.'], mistakes: ['Requesting a new code before the 60-second cooldown ends.', 'Using an expired or already-used code.', 'Entering a code for a different email address.'], troubleshooting: ['If the email does not arrive, check spam and wait for the resend timer.', 'If sending fails, ask the platform administrator to configure RESEND_API_KEY.', 'Use the latest code only; each code is single-use.'], faqs: [['How long is the OTP valid?', 'Five minutes from delivery.'], ['How often can I request a code?', 'Up to five times per email in one hour, with a 60-second cooldown between requests.']], tips: ['Keep your verified email current because it is used for account recovery and notifications.'] },
    hi: { title: 'ईमेल OTP सत्यापन', useful: 'Registration के बाद Resend द्वारा भेजे गए छह अंकों के one-time password से अपना email verify करें।', steps: ['Registration के बाद Verify Email खोलें।', 'अपना email address confirm करें।', 'Send verification code क्लिक करें।', 'Inbox में छह अंकों का OTP देखें।', 'पाँच मिनट के अंदर code डालकर Verify email क्लिक करें।'], mistakes: ['60-second cooldown खत्म होने से पहले नया code माँगना।', 'Expired या पहले use किया हुआ code डालना।', 'किसी दूसरे email का code डालना।'], troubleshooting: ['Email न मिले तो spam folder देखें और resend timer का इंतजार करें।', 'Send fail हो तो administrator से RESEND_API_KEY configure करने को कहें।', 'सिर्फ latest code use करें; हर code single-use होता है।'], faqs: [['OTP कितने समय तक valid है?', 'Delivery के बाद पाँच मिनट तक।'], ['Code कितनी बार मँगवा सकते हैं?', 'एक घंटे में एक email के लिए अधिकतम पाँच बार, हर request के बीच 60-second cooldown है।']], tips: ['Verified email को updated रखें; यही account recovery और notifications के लिए उपयोग होता है।'] }
  },
  {
    id: 'admin', paths: ['/admin', '/admin/login'], category: 'Administration',
    en: { title: 'Admin Portal and Verification', useful: 'Authorized Admins manage users, factory verification, listings, transactions, messages, audit logs, notifications, and platform health from the Admin Portal.', steps: ['Sign in through Admin Login with an authorized Admin or Super Admin account.', 'Use Users to search, update roles, suspend or activate accounts, and export user records.', 'Review Companies and factory documents before verifying a factory.', 'Use Listings, Marketplace, Transactions, and Chat Moderation for operational controls.', 'Review Audit Logs and System Health after every critical action.'], mistakes: ['Using a normal user account for admin routes.', 'Approving a factory before documents and address details are reviewed.', 'Sharing temporary password-reset values in public channels.'], troubleshooting: ['A 403 response means your account does not have an Admin role.', 'If data is stale, use Sync State.', 'If an action fails, review the displayed error and the Audit Logs.'], faqs: [['Who can access the Admin Portal?', 'Only Admin and Super Admin roles; all admin APIs enforce role-based access control.'], ['Are admin actions recorded?', 'Yes. Administrative changes are written to the audit trail with actor, action, timestamp, and IP information.']], tips: ['Use documented verification decisions to keep requests traceable.'] },
    hi: { title: 'Admin Portal और Verification', useful: 'Authorized Admins, Admin Portal से users, factory verification, listings, transactions, messages, audit logs, notifications और platform health manage करते हैं।', steps: ['Authorized Admin या Super Admin account से Admin Login करें।', 'Users में search, role update, suspend/activate और user export करें।', 'Factory verify करने से पहले Companies और documents review करें।', 'Operational control के लिए Listings, Marketplace, Transactions और Chat Moderation use करें।', 'महत्वपूर्ण action के बाद Audit Logs और System Health review करें।'], mistakes: ['Normal user account से admin routes खोलना।', 'Documents और address review किए बिना factory approve करना।', 'Temporary password-reset value को public channel में share करना।'], troubleshooting: ['403 response का मतलब account में Admin role नहीं है।', 'Data stale हो तो Sync State use करें।', 'Action fail हो तो displayed error और Audit Logs देखें।'], faqs: [['Admin Portal कौन access कर सकता है?', 'केवल Admin और Super Admin roles; सभी admin APIs पर RBAC लागू है।'], ['क्या admin actions record होते हैं?', 'हाँ। Actor, action, timestamp और IP information के साथ audit trail में लिखा जाता है।']], tips: ['Verification decisions को documented और traceable रखें।'] }
  },  {
    id: 'auth', paths: ['/login', '/register', '/forgot-password'], category: 'Account',
    en: { title: 'Login, Register, Google, and Recovery', useful: 'Sign in, register, request password recovery, and use Google OAuth when provider credentials are configured.', steps: ['Use email and password to sign in.', 'Use Remember Me if you want the email kept locally.', 'Use Sign in with Google after VITE_GOOGLE_CLIENT_ID and GOOGLE_CLIENT_ID are configured.', 'Use Forgot Password for recovery instructions.', 'Register if you do not have an account.'], mistakes: ['Using an unregistered email.', 'Expecting Google consent screens before provider credentials are configured.'], troubleshooting: ['If login fails, verify credentials.', 'If Google sign-in is unavailable, configure the Google client ID in frontend and backend environments.', 'If Google sign-in returns 401, verify the OAuth client ID matches the issued credential.'], faqs: [['Is Google sign-in available?', 'Yes. It uses real Google ID-token verification when Google OAuth client IDs are configured.'], ['Which roles exist?', 'Waste Producer, Raw Material Consumer, and Admin.']], tips: ['Use the role matching your workflow.'] },
    hi: { title: 'Login, Register, Google aur Recovery', useful: 'Sign in, register, password recovery request, aur configured Google OAuth use karein.', steps: ['Email aur password se sign in karein.', 'Email local rakhna ho to Remember Me use karein.', 'Google Sign-In ke liye VITE_GOOGLE_CLIENT_ID aur GOOGLE_CLIENT_ID configure karein.', 'Recovery instructions ke liye Forgot Password use karein.', 'Account na ho to Register karein.'], mistakes: ['Unregistered email use karna.', 'Provider credentials configure hone se pehle Google consent screen expect karna.'], troubleshooting: ['Login fail ho to credentials verify karein.', 'Google sign-in unavailable ho to frontend aur backend me Google client ID configure karein.', 'Google sign-in 401 de to OAuth client ID match verify karein.'], faqs: [['Kya Google sign-in available hai?', 'Haan. Google OAuth client IDs configured hone par real Google ID-token verification use hota hai.'], ['Kaunse roles hain?', 'Waste Producer, Raw Material Consumer, aur Admin.']], tips: ['Apne workflow ke hisab se role chunen.'] }
  }
];

function matchesDoc(doc, pathname) {
  return doc.paths.some((path) => pathname === path || (path !== '/' && pathname.startsWith(path)));
}

export default function HelpCenter() {
  const [open, setOpen] = useState(false);
  const [language, setLanguage] = useState('en');
  const [query, setQuery] = useState('');
  const [expanded, setExpanded] = useState(null);
  const location = useLocation();
  const navigate = useNavigate();

  const currentDoc = useMemo(() => docs.find((doc) => matchesDoc(doc, location.pathname)) || docs[0], [location.pathname]);
  const filteredDocs = docs.filter((doc) => {
    const copy = doc[language];
    const haystack = `${copy.title} ${copy.useful} ${doc.category}`.toLowerCase();
    return haystack.includes(query.toLowerCase());
  });
  const selected = filteredDocs.find((doc) => doc.id === currentDoc.id) || filteredDocs[0] || currentDoc;
  const copy = selected[language];
  const labels = language === 'hi'
    ? { search: 'Help खोजें', video: 'Guided walkthrough', steps: 'Step-by-step', mistakes: 'Common mistakes', trouble: 'Troubleshooting', faq: 'FAQs', tip: 'Tip' }
    : { search: 'Search help', video: 'Guided walkthrough', steps: 'Step-by-step', mistakes: 'Common mistakes', trouble: 'Troubleshooting', faq: 'FAQs', tip: 'Tip' };

  return (
    <>
      <button type="button" onClick={() => setOpen(true)} className="fixed bottom-5 right-5 z-40 inline-flex items-center gap-2 rounded-full bg-emerald-500 px-4 py-3 text-sm font-semibold text-slate-950 shadow-xl shadow-slate-950/30 transition hover:bg-emerald-400" aria-label="Open help center">
        <HelpCircle size={18} /> Help
      </button>

      {open ? (
        <div className="fixed inset-0 z-50 bg-slate-950/70 p-4 backdrop-blur-sm" role="dialog" aria-modal="true">
          <div className="mx-auto flex h-full max-w-6xl flex-col overflow-hidden rounded-2xl border border-slate-800 bg-slate-950 text-slate-100 shadow-2xl lg:max-h-[88vh] lg:flex-row">
            <aside className="border-b border-slate-800 p-4 lg:w-80 lg:border-b-0 lg:border-r">
              <div className="flex items-center justify-between gap-3">
                <div><p className="text-sm uppercase tracking-[0.25em] text-emerald-300">Help Center</p><h2 className="text-xl font-semibold text-white">SymbioAI Guide</h2></div>
                <button type="button" onClick={() => setOpen(false)} className="rounded-full border border-slate-700 p-2 text-slate-300 hover:text-white" aria-label="Close help center"><X size={18} /></button>
              </div>

              <div className="mt-4 flex rounded-full border border-slate-700 bg-slate-900 p-1 text-sm">
                <button type="button" onClick={() => setLanguage('en')} className={`flex-1 rounded-full px-3 py-2 ${language === 'en' ? 'bg-emerald-500 text-slate-950' : 'text-slate-300'}`}>English</button>
                <button type="button" onClick={() => setLanguage('hi')} className={`flex-1 rounded-full px-3 py-2 ${language === 'hi' ? 'bg-emerald-500 text-slate-950' : 'text-slate-300'}`}>हिन्दी</button>
              </div>

              <label className="mt-4 flex items-center gap-2 rounded-2xl border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-300"><Search size={16} /><input value={query} onChange={(event) => setQuery(event.target.value)} className="w-full bg-transparent outline-none" placeholder={labels.search} /></label>

              <div className="mt-4 space-y-2 overflow-y-auto lg:max-h-[55vh]">
                {filteredDocs.map((doc) => (
                  <button key={doc.id} type="button" onClick={() => { navigate(doc.paths[0] === '/' ? '/dashboard' : doc.paths[0]); setQuery(''); }} className={`w-full rounded-2xl border px-3 py-3 text-left text-sm transition ${doc.id === selected.id ? 'border-emerald-400/40 bg-emerald-500/10 text-emerald-200' : 'border-slate-800 bg-slate-900 text-slate-300 hover:border-slate-700'}`}>
                    <span className="block text-xs uppercase tracking-[0.2em] text-slate-500">{doc.category}</span>{doc[language].title}
                  </button>
                ))}
              </div>
            </aside>

            <main className="flex-1 overflow-y-auto p-5 lg:p-8">
              <div className="rounded-2xl border border-slate-800 bg-slate-900 p-4">
                <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                  <div><p className="text-sm uppercase tracking-[0.25em] text-emerald-300">{selected.category}</p><h3 className="mt-2 text-2xl font-semibold text-white">{copy.title}</h3><p className="mt-3 max-w-3xl text-sm leading-6 text-slate-300">{copy.useful}</p></div>
                  <div className="flex items-center gap-2 rounded-2xl border border-dashed border-slate-700 px-3 py-3 text-sm text-slate-400"><PlayCircle size={18} className="text-emerald-300" />{labels.video}</div>
                </div>
              </div>

              <section className="mt-5 grid gap-5 lg:grid-cols-[1fr_0.8fr]">
                <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5"><h4 className="font-semibold text-white">{labels.steps}</h4><ol className="mt-4 space-y-3 text-sm text-slate-300">{copy.steps.map((step, index) => <li key={step} className="flex gap-3"><span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-emerald-500 text-sm font-semibold text-slate-950">{index + 1}</span><span className="pt-1">{step}</span></li>)}</ol></div>
                <div className="space-y-5"><div className="rounded-2xl border border-slate-800 bg-slate-900 p-5"><h4 className="font-semibold text-white">{labels.mistakes}</h4><ul className="mt-3 space-y-2 text-sm text-slate-300">{copy.mistakes.map((item) => <li key={item}>- {item}</li>)}</ul></div><div className="rounded-2xl border border-slate-800 bg-slate-900 p-5"><h4 className="font-semibold text-white">{labels.trouble}</h4><ul className="mt-3 space-y-2 text-sm text-slate-300">{copy.troubleshooting.map((item) => <li key={item}>- {item}</li>)}</ul></div></div>
              </section>

              <section className="mt-5 rounded-2xl border border-slate-800 bg-slate-900 p-5"><h4 className="font-semibold text-white">{labels.faq}</h4><div className="mt-3 space-y-2">{copy.faqs.map(([question, answer], index) => <button key={question} type="button" onClick={() => setExpanded(expanded === index ? null : index)} className="w-full rounded-2xl border border-slate-800 bg-slate-950 px-4 py-3 text-left text-sm text-slate-300"><span className="flex items-center justify-between gap-3 font-medium text-white">{question}<ChevronDown size={16} className={expanded === index ? 'rotate-180 transition' : 'transition'} /></span>{expanded === index ? <span className="mt-2 block leading-6 text-slate-400">{answer}</span> : null}</button>)}</div></section>
              <section className="mt-5 grid gap-3 md:grid-cols-2">{copy.tips.map((tip) => <div key={tip} className="rounded-2xl border border-emerald-400/20 bg-emerald-500/10 p-4 text-sm text-emerald-200">{labels.tip}: {tip}</div>)}</section>
            </main>
          </div>
        </div>
      ) : null}
    </>
  );
}
