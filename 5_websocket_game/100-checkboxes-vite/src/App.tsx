import { useEffect, useState } from "react";
import useWebSocket from "react-use-websocket";

interface Checkbox {
  uuid: string;
  isChecked: boolean;
}

function App() {
  const [checkboxes, setCheckboxes] = useState<Checkbox[]>([]);

  const { sendMessage, lastMessage, readyState } = useWebSocket(
    import.meta.env.VITE_WS_URL || "ws://localhost:8000/api/v1/ws"
  );

  useEffect(() => {
    if (lastMessage !== null) {
      const data = JSON.parse(lastMessage.data);
      const action = data.action as string;

      if (action === "update_checkboxes") {
        setCheckboxes(data.data);
      } else if (action === "update_checkbox") {
        const { uuid, isChecked } = data.data;
        setCheckboxes((prevCheckboxes) => {
          return prevCheckboxes.map((checkbox) => {
            if (checkbox.uuid === uuid) {
              return { ...checkbox, isChecked };
            }
            return checkbox;
          });
        });
      }
    }
  }, [lastMessage]);

  return (
    <>
      <div className="container mx-auto p-4">
        <h1 className="text-2xl font-bold">100 Checkboxes</h1>
        <p>
          ติ๊กถูกให้ครบ 100 ช่อง... แค่นี้แหละ ง่าย ๆ ใช่ไหมล่ะ... ใช่สิ ถ้าไม่มี{" "}
          <strong>มารผจญ</strong>
        </p>

        <div className="text-right">
          <span className="text-xl">
            {checkboxes.filter((checkbox) => checkbox.isChecked).length}
          </span>{" "}
          <span className="text-sm text-neutral-500">/ {checkboxes.length}</span>
        </div>
        <div className="flex flex-wrap gap-4 mt-4">
          {/* {Array.from({ length: 100 }, (_, index) => (
            <input key={index} type="checkbox" className="w-12 h-12" />
          ))} */}
          {checkboxes.map((checkbox) => (
            <input
              key={checkbox.uuid}
              type="checkbox"
              className="w-12 h-12"
              checked={checkbox.isChecked}
              onChange={() => {
                sendMessage(
                  JSON.stringify({
                    action: "update_checkbox",
                    data: { uuid: checkbox.uuid, isChecked: !checkbox.isChecked },
                  })
                );
              }}
            />
          ))}
        </div>

        <div className="mt-4">#{readyState.toString()}</div>
      </div>
    </>
  );
}

export default App;
