import React from 'react';
import { AlertTriangle, ExternalLink } from 'lucide-react';

export function DataNotesBanner({ notes = [], verification }) {
  if (!notes.length || verification === 'verified') return null;
  return (
    <div
      role="status"
      className="mb-8 rounded-xl border border-amber-300 bg-amber-50 p-4 text-sm text-amber-900"
    >
      <div className="flex items-center gap-2 font-semibold mb-1">
        <AlertTriangle className="w-4 h-4" />
        {verification === 'not_found'
          ? 'We could not verify this school'
          : 'Please double-check these figures'}
      </div>
      <ul className="list-disc pl-5 space-y-1">
        {notes.map((note) => (
          <li key={note}>{note}</li>
        ))}
      </ul>
    </div>
  );
}

export function SourcesPanel({ sources = [], notes = [], verification, schoolNotes }) {
  const showNotes = verification === 'verified' ? notes : [];
  if (!sources.length && !showNotes.length && !schoolNotes) return null;

  return (
    <section className="mb-8 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <h2 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">
        Data Sources &amp; Notes
      </h2>

      {schoolNotes && <p className="text-sm text-slate-600 mb-3">{schoolNotes}</p>}

      {showNotes.length > 0 && (
        <ul className="list-disc pl-5 mb-3 space-y-1 text-sm text-slate-600">
          {showNotes.map((note) => (
            <li key={note}>{note}</li>
          ))}
        </ul>
      )}

      {sources.length > 0 && (
        <ul className="space-y-1.5 text-sm">
          {sources.map((source) => (
            <li key={source.url}>
              <a
                href={source.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 text-blue-700 hover:underline break-all"
              >
                <ExternalLink className="w-3.5 h-3.5 shrink-0" />
                {source.title}
              </a>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
