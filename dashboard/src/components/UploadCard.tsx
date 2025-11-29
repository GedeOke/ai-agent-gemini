type Props = {
  tags: string;
  onTagsChange: (v: string) => void;
  onFileChange: (file: File | null) => void;
  onUpload: () => void;
  uploading?: boolean;
};

export function UploadCard({ tags, onTagsChange, onFileChange, onUpload, uploading }: Props) {
  return (
    <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm">
      <div className="px-4 py-3 border-b border-slate-200 dark:border-slate-800">
        <h2 className="text-lg font-semibold">Upload Knowledge</h2>
      </div>
      <div className="p-4 grid gap-3 sm:grid-cols-2">
        <label className="flex flex-col gap-1 text-sm">
          <span className="text-slate-500 dark:text-slate-400">Tags</span>
          <input
            className="rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900 px-3 py-2"
            placeholder="produk,harga"
            value={tags}
            onChange={(e) => onTagsChange(e.target.value)}
          />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          <span className="text-slate-500 dark:text-slate-400">File</span>
          <input type="file" className="text-sm" onChange={(e) => onFileChange(e.target.files?.[0] || null)} />
        </label>
        <div className="col-span-full flex gap-2">
          <button
            onClick={onUpload}
            disabled={uploading}
            className="rounded-lg bg-primary text-white px-4 py-2 text-sm font-semibold hover:bg-primary-dark disabled:opacity-60"
          >
            {uploading ? "Uploading..." : "Upload"}
          </button>
        </div>
      </div>
    </div>
  );
}
