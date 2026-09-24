/**
 * The reviewer's item list - every row here already came back from
 * GET /items filtered to this reviewer (see ../api/client.js and
 * api/main.py's list_my_items()), so this component has no ownership
 * logic of its own to get right; it only renders what the API handed it.
 *
 * @param {{
 *   items: Array<{id: number, text: string, model_label: string, model_score: number, my_label: object|null}>,
 *   selectedId: number | null,
 *   onSelect: (id: number) => void,
 * }} props
 */
export default function ItemQueue({ items, selectedId, onSelect }) {
  return (
    <div className="flex flex-col gap-2">
      <p className="text-sm text-slate-500">
        {items.length} item{items.length === 1 ? '' : 's'} assigned to you.
      </p>
      {items.map((item) => {
        const isSelected = item.id === selectedId;
        const isLabeled = item.my_label !== null;
        return (
          <button
            key={item.id}
            onClick={() => onSelect(item.id)}
            className={`text-left rounded border p-3 transition-colors ${
              isSelected ? 'border-blue-500 bg-blue-50' : 'border-slate-200 bg-white hover:bg-slate-50'
            }`}
          >
            <div className="flex items-start justify-between gap-2">
              <p className="text-sm line-clamp-2">{item.text}</p>
              <span
                className={`shrink-0 text-xs rounded-full px-2 py-0.5 ${
                  isLabeled ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'
                }`}
              >
                {isLabeled ? 'Labeled' : 'Pending'}
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Model: <span className="font-mono">{item.model_label}</span> (
              {item.model_score.toFixed(2)})
            </p>
          </button>
        );
      })}
    </div>
  );
}
