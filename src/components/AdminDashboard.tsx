import React, { useEffect, useState } from "react";
import { db } from "../firebase";
import { collection, getDocs, doc, getDoc, setDoc } from "firebase/firestore";
import { getMonth, getDaysInMonth } from "../utils/dateUtils";

const AdminDashboard: React.FC = () => {
  const [users, setUsers] = useState<any[]>([]);
  const [availability, setAvailability] = useState<{ [userId: string]: any }>({});
  const [month, setMonth] = useState(() => getMonth());
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUsersAndAvailability = async () => {
      const usersSnap = await getDocs(collection(db, "users"));
      const usersList = usersSnap.docs.map(doc => ({ uid: doc.id, ...doc.data() }));
      setUsers(usersList);
      const avail: { [userId: string]: any } = {};
      for (const user of usersList) {
        const ref = doc(db, "availability", `${user.uid}_${month}`);
        const snap = await getDoc(ref);
        avail[user.uid] = snap.exists() ? snap.data() : { days: {}, adminOverrides: {} };
      }
      setAvailability(avail);
      setLoading(false);
    };
    fetchUsersAndAvailability();
  }, [month]);

  const handleOverrideChange = (userId: string, day: number, value: string) => {
    setAvailability(prev => ({
      ...prev,
      [userId]: {
        ...prev[userId],
        adminOverrides: {
          ...prev[userId].adminOverrides,
          [day]: value,
        },
      },
    }));
  };

  const handleSave = async (userId: string) => {
    const data = availability[userId];
    await setDoc(doc(db, "availability", `${userId}_${month}`), {
      ...data,
      userId,
      month,
    }, { merge: true });
    alert("Saved for user " + userId);
  };

  const daysInMonth = getDaysInMonth(month);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="overflow-x-auto p-4">
      <h2 className="text-xl font-bold mb-4 text-center">Admin: All Users' Availability ({month})</h2>
      <div className="flex gap-6">
        {users.map(user => (
          <div key={user.uid} className="min-w-[220px] border rounded p-2 bg-gray-50">
            <div className="font-semibold mb-2 text-center">{user.email}</div>
            <div className="grid grid-cols-1 gap-2 mb-2">
              {[...Array(daysInMonth)].map((_, i) => (
                <div key={i} className="flex flex-col items-center border rounded p-1 bg-white">
                  <div className="text-xs font-semibold">Day {i + 1}</div>
                  <div className="text-xs text-gray-500 mb-1">{availability[user.uid]?.days?.[i + 1] || "-"}</div>
                  <input
                    type="text"
                    className="w-20 p-1 border rounded text-xs"
                    value={availability[user.uid]?.adminOverrides?.[i + 1] || ""}
                    onChange={e => handleOverrideChange(user.uid, i + 1, e.target.value)}
                    placeholder="Override"
                  />
                </div>
              ))}
            </div>
            <button onClick={() => handleSave(user.uid)} className="bg-blue-600 text-white px-2 py-1 rounded text-xs hover:bg-blue-700">Save</button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AdminDashboard; 