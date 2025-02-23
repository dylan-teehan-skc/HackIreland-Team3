import React, { createContext, useState } from "react";

export const FileContext = createContext();

export const FileProvider = ({ children }) => {
  const [fileId, setFileId] = useState('');

  return (
    <FileContext.Provider value={{ fileId, setFileId }}>
      {children}
    </FileContext.Provider>
  );
}; 