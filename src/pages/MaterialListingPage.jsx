import { useEffect, useState } from 'react';
import { FileText, Image, RefreshCw, UploadCloud } from 'lucide-react';
import PageHeader from '../components/ui/PageHeader';
import api from '../services/api';
import { getApiError, unwrapData } from '../services/response';

const initialState = {
  materialName: '',
  composition: '',
  physicalState: 'Solid',
  quantity: '',
  frequency: 'Monthly',
};

const initialFiles = {
  certificate: null,
  photo: null,
  document: null,
};

function fileLabel(file, fallback) {
  return file ? `${file.name} (${Math.ceil(file.size / 1024)} KB)` : fallback;
}

async function createUploadUrl(file, purpose) {
  if (!file) return null;
  const response = await api.post('/storage/presign', {
    filename: file.name,
    content_type: file.type || 'application/octet-stream',
    purpose,
  });
  const upload = response.data?.data?.upload;
  await fetch(upload.upload_url, {
    method: 'PUT',
    headers: { 'Content-Type': file.type || 'application/octet-stream' },
    body: file,
  });
  return upload;
}

export default function MaterialListingPage() {
  const [form, setForm] = useState(initialState);
  const [files, setFiles] = useState(initialFiles);
  const [photoPreview, setPhotoPreview] = useState('');
  const [materials, setMaterials] = useState([]);
  const [errors, setErrors] = useState({});
  const [message, setMessage] = useState('');
  const [loadError, setLoadError] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const fetchMaterials = async () => {
    setLoading(true);
    setLoadError('');
    try {
      const response = await api.get('/materials');
      const data = unwrapData(response);
      setMaterials(data?.materials || []);
    } catch (error) {
      setLoadError(getApiError(error, 'Unable to load materials'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMaterials();
  }, []);

  useEffect(() => {
    if (!files.photo) {
      setPhotoPreview('');
      return undefined;
    }
    const url = URL.createObjectURL(files.photo);
    setPhotoPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [files.photo]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    setErrors((prev) => ({ ...prev, [name]: '' }));
    setMessage('');
  };

  const handleFileChange = (name) => (event) => {
    const file = event.target.files?.[0] || null;
    setFiles((prev) => ({ ...prev, [name]: file }));
    setErrors((prev) => ({ ...prev, [name]: '' }));
    setMessage('');
  };

  const validate = () => {
    const nextErrors = {};
    if (!form.materialName.trim()) nextErrors.materialName = 'Material name is required';
    if (!form.composition.trim()) nextErrors.composition = 'Chemical composition is required';
    if (!form.quantity.trim()) nextErrors.quantity = 'Quantity is required';
    if (!files.certificate) nextErrors.certificate = 'A certificate file is required';
    if (files.photo && !files.photo.type.startsWith('image/')) nextErrors.photo = 'Photo must be an image file';
    return nextErrors;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    const nextErrors = validate();
    setErrors(nextErrors);
    setMessage('');
    if (Object.keys(nextErrors).length > 0) return;

    setSubmitting(true);
    try {
      const attachmentSummary = [
        files.certificate ? `Certificate: ${files.certificate.name}` : '',
        files.photo ? `Photo: ${files.photo.name}` : '',
        files.document ? `Document: ${files.document.name}` : '',
      ].filter(Boolean).join(' | ');
      const [certificateUpload, photoUpload, documentUpload] = await Promise.all([
        createUploadUrl(files.certificate, 'certificates'),
        createUploadUrl(files.photo, 'waste-images'),
        createUploadUrl(files.document, 'lab-reports'),
      ]);

      const response = await api.post('/materials', {
        name: form.materialName.trim(),
        chemical_composition: form.composition.trim(),
        physical_state: form.physicalState,
        quantity: form.quantity.trim(),
        frequency: form.frequency,
        certificate: attachmentSummary,
        certificate_url: certificateUpload?.url || null,
        photo_url: photoUpload?.url || null,
        lab_report_url: documentUpload?.url || null,
        storage_provider: certificateUpload ? 's3' : null,
      });
      const saved = unwrapData(response)?.material;
      if (saved) setMaterials((prev) => [saved, ...prev]);
      setForm(initialState);
      setFiles(initialFiles);
      event.currentTarget.reset();
      setMessage('Files uploaded to object storage and listing saved to the database. AI matching is queued.');
    } catch (error) {
      setMessage(getApiError(error, 'Unable to submit listing'));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Material listing"
        description="Upload certificates, material photos, and documents for AI-powered industrial matching."
      />

      <div className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
        <div className="space-y-6">
          <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl shadow-slate-950/25">
            <h2 className="text-xl font-semibold text-white">Listing guidance</h2>
            <ul className="mt-4 space-y-3 text-sm leading-6 text-slate-400">
              <li>- Add exact chemical composition for better AI matching.</li>
              <li>- Upload certificate files such as PDF, JPG, or PNG.</li>
              <li>- Add a material photo and supporting document where available.</li>
            </ul>
          </div>

          <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl shadow-slate-950/25">
            <div className="flex items-center justify-between gap-3">
              <h2 className="text-xl font-semibold text-white">Saved listings</h2>
              <button type="button" onClick={fetchMaterials} className="inline-flex items-center gap-2 rounded-full border border-slate-700 px-3 py-2 text-sm text-slate-300 hover:border-emerald-400 hover:text-emerald-300">
                <RefreshCw size={15} /> Refresh
              </button>
            </div>

            {loading ? <p className="mt-4 text-sm text-slate-400">Loading materials...</p> : null}
            {loadError ? <p className="mt-4 rounded-2xl border border-rose-500/30 bg-rose-500/10 p-3 text-sm text-rose-300">{loadError}</p> : null}
            {!loading && !loadError && materials.length === 0 ? (
              <p className="mt-4 rounded-2xl border border-dashed border-slate-700 p-4 text-sm text-slate-400">No materials yet. Submit your first listing to start matching.</p>
            ) : null}
            <div className="mt-4 space-y-3">
              {materials.slice(0, 5).map((material) => (
                <div key={material.id} className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="font-medium text-white">{material.name}</p>
                      <p className="mt-1 text-sm text-slate-400">{material.quantity} - {material.frequency}</p>
                    </div>
                    <span className="rounded-full bg-emerald-500/10 px-3 py-1 text-xs text-emerald-300">{material.status}</span>
                  </div>
                  <p className="mt-2 text-sm text-slate-400">{material.chemical_composition}</p>
                  {material.certificate ? <p className="mt-2 text-xs text-slate-500">Uploads: {material.certificate}</p> : null}
                </div>
              ))}
            </div>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl shadow-slate-950/25">
          <div className="grid gap-4 md:grid-cols-2">
            <label className="space-y-2 text-sm text-slate-300">
              <span>Material Name</span>
              <input name="materialName" value={form.materialName} onChange={handleChange} className="w-full rounded-2xl border border-slate-700 bg-slate-950/70 px-4 py-3 text-white outline-none" placeholder="Blast furnace slag" />
              {errors.materialName ? <p className="text-sm text-rose-400">{errors.materialName}</p> : null}
            </label>

            <label className="space-y-2 text-sm text-slate-300">
              <span>Physical State</span>
              <select name="physicalState" value={form.physicalState} onChange={handleChange} className="w-full rounded-2xl border border-slate-700 bg-slate-950/70 px-4 py-3 text-white outline-none">
                <option>Solid</option>
                <option>Liquid</option>
                <option>Gas</option>
                <option>Heat</option>
              </select>
            </label>

            <label className="space-y-2 text-sm text-slate-300 md:col-span-2">
              <span>Chemical Composition</span>
              <textarea name="composition" value={form.composition} onChange={handleChange} rows="3" className="w-full rounded-2xl border border-slate-700 bg-slate-950/70 px-4 py-3 text-white outline-none" placeholder="SiO2 38%, CaO 24%, Fe2O3 18%" />
              {errors.composition ? <p className="text-sm text-rose-400">{errors.composition}</p> : null}
            </label>

            <label className="space-y-2 text-sm text-slate-300">
              <span>Quantity</span>
              <input name="quantity" value={form.quantity} onChange={handleChange} className="w-full rounded-2xl border border-slate-700 bg-slate-950/70 px-4 py-3 text-white outline-none" placeholder="1,200 tons" />
              {errors.quantity ? <p className="text-sm text-rose-400">{errors.quantity}</p> : null}
            </label>

            <label className="space-y-2 text-sm text-slate-300">
              <span>Frequency</span>
              <select name="frequency" value={form.frequency} onChange={handleChange} className="w-full rounded-2xl border border-slate-700 bg-slate-950/70 px-4 py-3 text-white outline-none">
                <option>Weekly</option>
                <option>Monthly</option>
                <option>Quarterly</option>
              </select>
            </label>

            <label className="space-y-2 text-sm text-slate-300 md:col-span-2">
              <span>Upload Certificate</span>
              <div className="flex items-center gap-3 rounded-2xl border border-dashed border-slate-700 bg-slate-950/70 px-4 py-5">
                <UploadCloud size={18} className="text-emerald-300" />
                <input type="file" accept=".pdf,.png,.jpg,.jpeg" onChange={handleFileChange('certificate')} className="w-full text-sm text-slate-300 file:mr-4 file:rounded-full file:border-0 file:bg-emerald-500 file:px-4 file:py-2 file:font-semibold file:text-slate-950" />
              </div>
              <p className="text-xs text-slate-500">{fileLabel(files.certificate, 'PDF, PNG, or JPG certificate')}</p>
              {errors.certificate ? <p className="text-sm text-rose-400">{errors.certificate}</p> : null}
            </label>

            <label className="space-y-2 text-sm text-slate-300">
              <span>Material Photo</span>
              <div className="rounded-2xl border border-dashed border-slate-700 bg-slate-950/70 p-4">
                <div className="mb-3 flex items-center gap-2 text-slate-400"><Image size={17} /> Photo upload</div>
                <input type="file" accept="image/*" onChange={handleFileChange('photo')} className="w-full text-sm text-slate-300 file:mr-4 file:rounded-full file:border-0 file:bg-slate-800 file:px-4 file:py-2 file:font-semibold file:text-slate-200" />
                {photoPreview ? <img src={photoPreview} alt="Selected material preview" className="mt-3 h-28 w-full rounded-xl object-cover" /> : null}
              </div>
              {errors.photo ? <p className="text-sm text-rose-400">{errors.photo}</p> : null}
            </label>

            <label className="space-y-2 text-sm text-slate-300">
              <span>Supporting Document</span>
              <div className="rounded-2xl border border-dashed border-slate-700 bg-slate-950/70 p-4">
                <div className="mb-3 flex items-center gap-2 text-slate-400"><FileText size={17} /> Document upload</div>
                <input type="file" accept=".pdf,.doc,.docx,.xls,.xlsx,.csv,.txt" onChange={handleFileChange('document')} className="w-full text-sm text-slate-300 file:mr-4 file:rounded-full file:border-0 file:bg-slate-800 file:px-4 file:py-2 file:font-semibold file:text-slate-200" />
                <p className="mt-3 text-xs text-slate-500">{fileLabel(files.document, 'Optional technical sheet or lab report')}</p>
              </div>
            </label>
          </div>

          <button type="submit" disabled={submitting} className="mt-6 rounded-full bg-emerald-500 px-5 py-3 font-semibold text-slate-950 transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-70">
            {submitting ? 'Submitting...' : 'Submit listing'}
          </button>

          {message ? <p className={`mt-4 text-sm ${message.includes('Unable') ? 'text-rose-300' : 'text-emerald-300'}`}>{message}</p> : null}
        </form>
      </div>
    </div>
  );
}
