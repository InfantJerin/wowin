interface FormGroupProps {
  label: string;
  id: string;
  type?: string;
  placeholder?: string;
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

export const FormGroup = ({ 
  label, 
  id, 
  type = 'text', 
  placeholder = '', 
  value = '',
  onChange 
}: FormGroupProps) => {
  return (
    <div className="form-group">
      <label htmlFor={id}>{label}</label>
      <input
        type={type}
        id={id}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
      />
    </div>
  );
}; 