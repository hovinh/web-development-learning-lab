import { useEffect, useState } from 'react';

const DECISIONS = [
  { key: '1', value: 'correct', label: 'Correct' },
  { key: '2', value: 'incorrect', label: 'Incorrect' },
  { key: '3', value: 'unsure', label: 'Unsure' },
];

/**
 * The currently-selected item, plus its decision buttons and 1/2/3
 * keyboard shortcuts. This whole component - and App.jsx's
 * auto-advance-to-the-next-item behavior it triggers - is the specific
 * "smooth, instant updates, no reloads" payoff the blog names as the
 * reason to reach for this stack over Django in the first place; see
 * ../../README.md's "Interactivity" section.
 *
 * @param {{
 *   item: {id: number, text: string, model_label: string, model_score: number, my_label: object|null},
 *   onLabel: (data: {decision: string, corrected_label: string}) => void,
 *   submitting: boolean,
 * }} props
 */
export default function LabelPanel({ item, onLabel, submitting }) {
  const [correctedLabel, setCorrectedLabel] = useState('');

  // Clear the "corrected label" input whenever the reviewer moves to a
  // different item (via auto-advance or clicking another row in
  // ItemQueue), so stale text from the previous item never gets
  // attached to this one.
  useEffect(() => {
    setCorrectedLabel('');
  }, [item.id]);

  const submit = (decision) => onLabel({ decision, corrected_label: correctedLabel });

  useEffect(() => {
    function handleKeyDown(event) {
      // Don't hijack 1/2/3 while the reviewer is typing in the
      // corrected-label input below.
      if (event.target.tagName === 'INPUT') return;

      const match = DECISIONS.find((decision) => decision.key === event.key);
      if (match) submit(match.value);
    }

    window.addEventListener('keydown', handleKeyDown);
    // Re-bind on every render so the listener's closure always has the
    // current item/correctedLabel - the alternative (a ref) would work
    // too, but this keeps submit() itself simple.
    return () => window.removeEventListener('keydown', handleKeyDown);
  });

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <h2 className="text-lg font-bold mb-1">Ticket #{item.id}</h2>
      <p className="my-3">{item.text}</p>
      <p className="text-sm text-slate-500 mb-4">
        Model predicted <span className="font-mono">{item.model_label}</span> with{' '}
        {item.model_score.toFixed(2)} confidence.
      </p>

      {item.my_label && (
        <p className="text-sm text-green-700 mb-3">
          Already labeled: <strong>{item.my_label.decision}</strong>
          {item.my_label.corrected_label && ` (${item.my_label.corrected_label})`}
        </p>
      )}

      <label className="block text-sm font-medium mb-3">
        Corrected label (only needed if marking Incorrect)
        <input
          className="mt-1 w-full border rounded px-3 py-2"
          value={correctedLabel}
          onChange={(event) => setCorrectedLabel(event.target.value)}
        />
      </label>

      <div className="flex gap-2">
        {DECISIONS.map((decision) => (
          <button
            key={decision.value}
            onClick={() => submit(decision.value)}
            disabled={submitting}
            className="flex-1 border rounded px-3 py-2 font-medium hover:bg-slate-50 disabled:opacity-60"
          >
            {decision.label} <span className="text-slate-400 text-xs">({decision.key})</span>
          </button>
        ))}
      </div>
    </div>
  );
}
