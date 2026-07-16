import { useEffect, useMemo, useRef, useState } from 'react';
import { ArrowRight, CheckCircle2, FileText, MessageSquare, Paperclip, Send, X } from 'lucide-react';
import PageHeader from '../components/ui/PageHeader';
import api from '../services/api';
import { aiMatches as fallbackMatches } from '../services/dummyData';
import { getApiError, unwrapData } from '../services/response';

function normalizeMatch(match, index) {
  return {
    id: match.id || `fallback-${index}`,
    name: match.name || match.material_name || match.summary || `Material match ${index + 1}`,
    partner: match.partner || match.partner_name || 'Verified buyer',
    score: match.score || match.symbio_score || 0,
    distance: match.distance || `${match.distance_km || 0} km`,
    carbon: match.carbon || match.carbon_savings || 'Impact pending',
    summary: match.summary || 'AI found a compatible industrial symbiosis opportunity.',
  };
}

export default function AiMatchPage() {
  const [matches, setMatches] = useState([]);
  const [selectedMatch, setSelectedMatch] = useState(null);
  const [activeConversation, setActiveConversation] = useState(null);
  const [conversations, setConversations] = useState([]);
  const [messages, setMessages] = useState([]);
  const [message, setMessage] = useState('');
  const [draft, setDraft] = useState('');
  const [offerAmount, setOfferAmount] = useState('');
  const [attachment, setAttachment] = useState(null);
  const [notice, setNotice] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [realtimeStatus, setRealtimeStatus] = useState('offline');
  const [typing, setTyping] = useState(false);
  const socketRef = useRef(null);
  const reconnectRef = useRef(null);

  const unreadCount = useMemo(() => conversations.reduce((total, item) => total + (item.unread_count || 0), 0), [conversations]);

  const fetchMatches = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await api.get('/matches');
      const data = unwrapData(response);
      const liveMatches = (data?.matches || []).map(normalizeMatch);
      setMatches(liveMatches.length ? liveMatches : fallbackMatches.map(normalizeMatch));
    } catch (err) {
      setMatches(fallbackMatches.map(normalizeMatch));
      setError(getApiError(err, 'Live matches could not load. Showing local matches.'));
    } finally {
      setLoading(false);
    }
  };

  const fetchConversations = async () => {
    try {
      const response = await api.get('/messaging/conversations');
      setConversations(unwrapData(response)?.conversations || []);
    } catch (err) {
      setError(getApiError(err, 'Unable to load conversations'));
    }
  };

  const fetchMessages = async (conversationId) => {
    try {
      const response = await api.get(`/messaging/conversations/${conversationId}/messages`);
      setMessages(unwrapData(response)?.messages || []);
      fetchConversations();
    } catch (err) {
      setError(getApiError(err, 'Unable to load messages'));
    }
  };

  useEffect(() => {
    fetchMatches();
    fetchConversations();
  }, []);

  useEffect(() => {
    const token = localStorage.getItem('symbioai_token');
    if (!token) return undefined;

    const connect = () => {
      const apiBase = import.meta.env.VITE_API_URL || '/api';
      const wsBase = apiBase.startsWith('http')
        ? apiBase.replace(/^http/, 'ws').replace(/\/api$/, '')
        : `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}`;
      const socket = new WebSocket(`${wsBase}/api/messaging/ws?token=${encodeURIComponent(token)}`);
      socketRef.current = socket;
      socket.onopen = () => setRealtimeStatus('online');
      socket.onclose = () => {
        setRealtimeStatus('reconnecting');
        reconnectRef.current = window.setTimeout(connect, 2500);
      };
      socket.onerror = () => setRealtimeStatus('reconnecting');
      socket.onmessage = (event) => {
        const payload = JSON.parse(event.data);
        if (payload.type === 'message' && activeConversation?.id === payload.conversation_id) {
          setMessages((prev) => prev.some((item) => item.id === payload.message.id) ? prev : [...prev, payload.message]);
        }
        if (payload.type === 'offer' && activeConversation?.id === payload.conversation_id) {
          setMessages((prev) => prev.some((item) => item.id === payload.message.id) ? prev : [...prev, payload.message]);
        }
        if (payload.type === 'typing') {
          setTyping(true);
          window.setTimeout(() => setTyping(false), 1800);
        }
        if (payload.type === 'notification') {
          setNotice(payload.notification.message);
          fetchConversations();
        }
      };
    };

    connect();
    return () => {
      if (reconnectRef.current) window.clearTimeout(reconnectRef.current);
      socketRef.current?.close();
    };
  }, [activeConversation?.id]);

  useEffect(() => {
    if (!activeConversation) return undefined;
    const intervalId = window.setInterval(() => fetchMessages(activeConversation.id), 8000);
    return () => window.clearInterval(intervalId);
  }, [activeConversation]);

  const openContact = (match) => {
    setSelectedMatch(match);
    setMessage(`Hello ${match.partner}, I am interested in discussing the ${match.name} opportunity. Can we review specifications, pricing, and shipment timing?`);
    setNotice('');
    setError('');
  };

  const createConversation = async (event) => {
    event.preventDefault();
    if (!selectedMatch) return;
    setSubmitting(true);
    setError('');
    setNotice('');
    try {
      const response = await api.post('/messaging/conversations', {
        match_id: selectedMatch.id,
        material_name: selectedMatch.name,
        partner_name: selectedMatch.partner,
        message,
      });
      const conversation = unwrapData(response)?.conversation;
      setSelectedMatch(null);
      setActiveConversation(conversation);
      setDraft('');
      await fetchConversations();
      await fetchMessages(conversation.id);
      setNotice(`Negotiation thread opened with ${selectedMatch.partner}.`);
    } catch (err) {
      setError(getApiError(err, 'Unable to create negotiation thread'));
    } finally {
      setSubmitting(false);
    }
  };

  const openConversation = async (conversation) => {
    setActiveConversation(conversation);
    setDraft('');
    setOfferAmount('');
    setAttachment(null);
    setNotice('');
    setError('');
    await fetchMessages(conversation.id);
  };

  const sendChatMessage = async (event) => {
    event.preventDefault();
    if (!activeConversation || !draft.trim()) return;
    setSubmitting(true);
    try {
      const response = await api.post(`/messaging/conversations/${activeConversation.id}/messages`, {
        body: draft.trim(),
        attachment_name: attachment?.name || null,
        attachment_type: attachment?.type || null,
      });
      const saved = unwrapData(response)?.message;
      setMessages((prev) => [...prev, saved]);
      setDraft('');
      setAttachment(null);
      await fetchConversations();
    } catch (err) {
      setError(getApiError(err, 'Unable to send message'));
    } finally {
      setSubmitting(false);
    }
  };

  const sendTyping = () => {
    if (socketRef.current?.readyState === WebSocket.OPEN && activeConversation) {
      socketRef.current.send(JSON.stringify({ type: 'typing', conversation_id: activeConversation.id }));
    }
  };

  const updateOffer = async (status) => {
    if (!activeConversation) return;
    setSubmitting(true);
    try {
      const response = await api.put(`/messaging/conversations/${activeConversation.id}/offer`, {
        status,
        offer_amount: offerAmount,
      });
      const data = unwrapData(response);
      setMessages((prev) => [...prev, data.message]);
      setActiveConversation(data.conversation);
      setOfferAmount('');
      await fetchConversations();
    } catch (err) {
      setError(getApiError(err, 'Unable to update offer'));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="AI match engine"
        description="Review high-confidence pairings and negotiate with buyers through persistent marketplace messaging."
      />

      {notice ? (
        <div className="flex items-center gap-3 rounded-2xl border border-emerald-400/30 bg-emerald-500/10 p-4 text-sm text-emerald-200">
          <CheckCircle2 size={18} />
          {notice}
        </div>
      ) : null}
      {error ? <div className="rounded-2xl border border-rose-500/30 bg-rose-500/10 p-4 text-sm text-rose-200">{error}</div> : null}

      <section className="grid gap-6 xl:grid-cols-[1fr_0.42fr]">
        <div className="grid gap-4">
          {loading ? <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 text-slate-300">Loading AI matches...</div> : null}
          {matches.map((match) => (
            <div key={match.id} className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl shadow-slate-950/25">
              <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                <div>
                  <p className="text-sm font-medium uppercase tracking-[0.3em] text-emerald-300">Match ready</p>
                  <h2 className="mt-2 text-2xl font-semibold text-white">{match.name}</h2>
                  <p className="mt-2 text-sm text-slate-400">Partner: {match.partner}</p>
                  <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-400">{match.summary}</p>
                </div>
                <div className="rounded-2xl border border-emerald-400/20 bg-emerald-500/10 px-4 py-3 text-emerald-300">
                  Symbio Score {match.score}/100
                </div>
              </div>

              <div className="mt-6 grid gap-4 md:grid-cols-4">
                <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
                  <p className="text-sm text-slate-400">Distance</p>
                  <p className="mt-2 text-lg font-semibold text-white">{match.distance}</p>
                </div>
                <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
                  <p className="text-sm text-slate-400">Carbon savings</p>
                  <p className="mt-2 text-lg font-semibold text-white">{match.carbon}</p>
                </div>
                <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
                  <p className="text-sm text-slate-400">Confidence</p>
                  <p className="mt-2 text-lg font-semibold text-white">{Math.min(99, Number(match.score) + 1)}%</p>
                </div>
                <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
                  <p className="text-sm text-slate-400">Next action</p>
                  <button type="button" onClick={() => openContact(match)} className="mt-2 inline-flex items-center gap-2 rounded-full bg-emerald-500 px-3 py-2 text-sm font-semibold text-slate-950 transition hover:bg-emerald-400">
                    Contact buyer
                    <ArrowRight size={16} />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        <aside className="rounded-3xl border border-slate-800 bg-slate-900/80 p-5 shadow-xl shadow-slate-950/25">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.25em] text-emerald-300">Messenger</p>
              <h2 className="mt-1 text-xl font-semibold text-white">Negotiations</h2>
            </div>
            <span className="rounded-full bg-emerald-500/10 px-3 py-1 text-sm text-emerald-300">{unreadCount} unread</span>
          </div>
          <div className="mt-5 space-y-3">
            {conversations.length === 0 ? (
              <div className="rounded-2xl border border-dashed border-slate-700 p-4 text-sm text-slate-400">No conversations yet. Contact a buyer to open a thread.</div>
            ) : null}
            {conversations.map((conversation) => (
              <button key={conversation.id} type="button" onClick={() => openConversation(conversation)} className="w-full rounded-2xl border border-slate-800 bg-slate-950/70 p-4 text-left transition hover:border-emerald-400/40">
                <div className="flex items-center justify-between gap-3">
                  <p className="font-semibold text-white">{conversation.partner_name}</p>
                  <span className="rounded-full bg-slate-800 px-2 py-0.5 text-xs text-slate-300">{conversation.status}</span>
                </div>
                <p className="mt-1 text-sm text-slate-400">{conversation.material_name}</p>
                <p className="mt-2 text-xs text-emerald-300">Online now</p>
              </button>
            ))}
          </div>
        </aside>
      </section>

      {selectedMatch ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/75 p-4 backdrop-blur-sm">
          <form onSubmit={createConversation} className="w-full max-w-xl rounded-3xl border border-slate-800 bg-slate-950 p-6 shadow-2xl">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-sm uppercase tracking-[0.25em] text-emerald-300">Negotiation</p>
                <h3 className="mt-2 text-2xl font-semibold text-white">Contact {selectedMatch.partner}</h3>
                <p className="mt-2 text-sm text-slate-400">Create a persistent buyer/seller thread for {selectedMatch.name}.</p>
              </div>
              <button type="button" onClick={() => setSelectedMatch(null)} className="rounded-full border border-slate-700 p-2 text-slate-300 hover:text-white" aria-label="Close contact buyer modal">
                <X size={18} />
              </button>
            </div>

            <label className="mt-5 block text-sm text-slate-300">
              Message
              <textarea value={message} onChange={(event) => setMessage(event.target.value)} rows="5" required className="mt-2 w-full rounded-2xl border border-slate-700 bg-slate-900 px-4 py-3 text-white outline-none" />
            </label>

            <div className="mt-5 flex flex-wrap gap-3">
              <button type="submit" disabled={submitting} className="inline-flex items-center gap-2 rounded-full bg-emerald-500 px-5 py-3 font-semibold text-slate-950 hover:bg-emerald-400 disabled:opacity-70">
                <MessageSquare size={17} /> {submitting ? 'Opening thread...' : 'Open messenger'}
              </button>
              <button type="button" onClick={() => setSelectedMatch(null)} className="rounded-full border border-slate-700 px-5 py-3 text-slate-300 hover:border-slate-500">
                Cancel
              </button>
            </div>
          </form>
        </div>
      ) : null}

      {activeConversation ? (
        <div className="fixed bottom-5 right-5 z-50 flex h-[78vh] w-[min(94vw,520px)] flex-col overflow-hidden rounded-3xl border border-emerald-400/20 bg-slate-950 shadow-2xl shadow-slate-950/50">
          <header className="border-b border-slate-800 bg-slate-900/90 p-4">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-xs uppercase tracking-[0.25em] text-emerald-300">Live negotiation</p>
                <h3 className="mt-1 text-lg font-semibold text-white">{activeConversation.partner_name}</h3>
                <p className="text-sm text-slate-400">{activeConversation.material_name}</p>
              </div>
              <button type="button" onClick={() => setActiveConversation(null)} className="rounded-full border border-slate-700 p-2 text-slate-300 hover:text-white" aria-label="Close messenger">
                <X size={18} />
              </button>
            </div>
            <div className="mt-3 flex items-center gap-2 text-xs text-emerald-300">
              <span className="h-2 w-2 rounded-full bg-emerald-400" />
              Realtime {realtimeStatus} {typing ? '- buyer typing...' : '- read receipts enabled'}
            </div>
          </header>

          <div className="flex-1 space-y-3 overflow-y-auto p-4">
            {messages.map((item) => (
              <div key={item.id} className="ml-auto max-w-[86%] rounded-2xl border border-emerald-400/20 bg-emerald-500/10 p-3 text-sm text-slate-100">
                <div className="mb-1 flex items-center justify-between gap-3 text-xs text-slate-400">
                  <span>{item.sender_name}</span>
                  <span>{item.created_at ? new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Now'}</span>
                </div>
                <p className="leading-6">{item.body}</p>
                {item.attachment_name ? <p className="mt-2 inline-flex items-center gap-1 text-xs text-emerald-200"><FileText size={14} /> {item.attachment_name}</p> : null}
                {item.offer_amount ? <p className="mt-2 rounded-xl bg-slate-950/70 px-3 py-2 text-xs text-emerald-200">Offer: {item.offer_amount} - {item.offer_status}</p> : null}
              </div>
            ))}
          </div>

          <div className="border-t border-slate-800 bg-slate-900/95 p-4">
            <div className="mb-3 grid gap-2 sm:grid-cols-[1fr_auto_auto_auto]">
              <input value={offerAmount} onChange={(event) => setOfferAmount(event.target.value)} className="rounded-2xl border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white outline-none" placeholder="Offer amount" />
              <button type="button" onClick={() => updateOffer('accepted')} disabled={submitting} className="rounded-2xl bg-emerald-500 px-3 py-2 text-sm font-semibold text-slate-950 disabled:opacity-60">Accept</button>
              <button type="button" onClick={() => updateOffer('countered')} disabled={submitting} className="rounded-2xl border border-amber-400/40 px-3 py-2 text-sm font-semibold text-amber-200 disabled:opacity-60">Counter</button>
              <button type="button" onClick={() => updateOffer('rejected')} disabled={submitting} className="rounded-2xl border border-rose-400/40 px-3 py-2 text-sm font-semibold text-rose-200 disabled:opacity-60">Reject</button>
            </div>
            <form onSubmit={sendChatMessage} className="flex items-center gap-2">
              <label className="rounded-2xl border border-slate-700 p-3 text-slate-300 hover:text-white">
                <Paperclip size={18} />
                <input type="file" accept=".pdf,.png,.jpg,.jpeg,.doc,.docx" onChange={(event) => setAttachment(event.target.files?.[0] || null)} className="hidden" />
              </label>
              <input value={draft} onChange={(event) => { setDraft(event.target.value); sendTyping(); }} className="min-w-0 flex-1 rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white outline-none" placeholder={attachment ? `Attached: ${attachment.name}` : 'Write a message...'} />
              <button type="submit" disabled={submitting || !draft.trim()} className="rounded-2xl bg-emerald-500 p-3 text-slate-950 disabled:opacity-60" aria-label="Send message">
                <Send size={18} />
              </button>
            </form>
          </div>
        </div>
      ) : null}
    </div>
  );
}
