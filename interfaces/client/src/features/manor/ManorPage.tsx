import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

interface Land {
  land_index: number;
  status: number;
  tree_type: number;
  remaining_seconds: number;
  is_mature: boolean;
}

export const ManorPage: React.FC = () => {
  const navigate = useNavigate();
  const [lands, setLands] = useState<Land[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/manor/status')
      .then(res => res.json())
      .then(data => {
        if (data.ok) {
          setLands(data.lands || []);
        }
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  return (
    <div className="p-4 bg-[#fdf5d6] min-h-screen font-sans text-sm">
      <div className="mb-4">
        <div className="text-lg font-bold mb-2">【庄园】 <span className="text-blue-600 cursor-pointer">简介</span></div>
        <div className="mb-2">风水:青山绿水</div>
        <div className="flex items-center gap-2">
          <span>[{lands.length}块庄园土地]</span>
          <span className="text-blue-600 cursor-pointer">扩建</span>
        </div>
      </div>

      {lands.length === 0 && !loading && (
        <div className="text-gray-500 py-4">暂无土地，点击扩建开始经营</div>
      )}

      <div className="grid grid-cols-1 gap-4 mb-8">
        {lands.map((land) => (
          <div key={land.land_index} className="border-b border-dashed border-gray-400 pb-2">
            土地 #{land.land_index + 1}: {land.status === 0 ? '未开启' : land.status === 1 ? '空闲' : '种植中'}
          </div>
        ))}
      </div>

      <div className="mt-8 border-t border-gray-300 pt-4 text-center">
        <span 
          className="text-blue-600 cursor-pointer text-lg hover:underline"
          onClick={() => navigate('/main')}
        >
          返回游戏首页
        </span>
      </div>
    </div>
  );
};
