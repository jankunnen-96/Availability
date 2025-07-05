import React, { useEffect, useState } from "react";
import { auth, db } from "../firebase";
import { doc, getDoc, setDoc } from "firebase/firestore";
import { getMonth, getDaysInMonth } from "../utils/dateUtils";

const Calendar: React.FC = () => {
  const [days, setDays] = useState<{ [key: string]: string }>({});
  const [overrides, setOverrides] = useState<{ [key: string]: string }>({});
  const [loading, setLoading] = useState(true);
  const [month, setMonth] = useState(() => getMonth());
  const [userId, setUserId] = useState<string | null>(null);

  useEffect(() => {
    const user = auth.currentUser;
    if (!user) return;
    setUserId(user.uid);
    const fetchData = async () => {
      const ref = doc(db, "availability", `${user.uid}_${month}`);
      const snap = await getDoc(ref);
      if (snap.exists()) {
        setDays(snap.data().days || {});
        setOverrides(snap.data().adminOverrides || {});
      }
      setLoading(false);
    };
    fetchData();
  }, [month]);

  const handleChange = (day: number, value: string) => {
    setDays(prev => ({ ...prev, [day]: value }));
  };

  const handleSave = async () => {
    if (!userId) return;
    await setDoc(doc(db, "availability", `${userId}_${month}`), {
      userId,
      month,
      days,
      adminOverrides: overrides,
    }, { merge: true });
    alert("Saved!");
  };

  const daysInMonth = getDaysInMonth(month);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h2 className="text-xl font-bold mb-4 text-center">Your Availability ({month})</h2>
      <div className="grid grid-cols-7 gap-2 mb-4">
        {[...Array(daysInMonth)].map((_, i) => (
          <div key={i} className="flex flex-col items-center border rounded p-2 bg-gray-50">
            <div className="font-semibold mb-1">{i + 1}</div>
            {overrides[i + 1] ? (
              <div className="text-red-600 text-xs">{overrides[i + 1]}</div>
            ) : (
              <input
                type="text"
                className="w-16 p-1 border rounded text-xs"
                value={days[i + 1] || ""}
                onChange={e => handleChange(i + 1, e.target.value)}
                placeholder="e.g. 9-12"
              />
            )}
          </div>
        ))}
      </div>
      <button onClick={handleSave} className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">Save</button>
    </div>
  );
};

export default Calendar; 