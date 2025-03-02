// DynamicForm.jsx
import React, { useState, useEffect, useContext } from 'react';
import { FormContext } from '../context/FormContext';
import { CollaborationContext } from '../context/CollaborationContext';
import FormSection from './FormSection';
import FormControls from './FormControls';

const DynamicForm = ({ formConfig, initialValues = {}, onSubmit, readOnly = false }) => {
  const [formValues, setFormValues] = useState({});
  const [activeTab, setActiveTab] = useState('');
  const [errors, setErrors] = useState({});
  const [isDirty, setIsDirty] = useState(false);
  
  const { registerForm, unregisterForm } = useContext(FormContext);
  const { 
    isCollaborative, 
    shareChanges, 
    receiveChanges,
    usersEditingFields 
  } = useContext(CollaborationContext);
  
  // Initialize form with configuration and initial values
  useEffect(() => {
    if (formConfig) {
      // Set default values from config
      const defaultValues = {};
      formConfig.fields.forEach(field => {
        if (field.defaultValue !== undefined) {
          defaultValues[field.id] = field.defaultValue;
        } else {
          defaultValues[field.id] = '';
        }
      });
      
      // Override with initial values if provided
      setFormValues({ ...defaultValues, ...initialValues });
      
      // Set first tab as active
      if (formConfig.layout.type === 'tabbed' && formConfig.layout.tabs.length > 0) {
        setActiveTab(formConfig.layout.tabs[0].id);
      }
      
      // Register form with context
      if (formConfig.formId) {
        registerForm(formConfig.formId, {
          getValues: () => formValues,
          setValues: (newValues) => setFormValues(prev => ({ ...prev, ...newValues })),
          validate: validateForm,
          reset: () => setFormValues(defaultValues)
        });
      }
    }
    
    return () => {
      // Cleanup on unmount
      if (formConfig?.formId) {
        unregisterForm(formConfig.formId);
      }
    };
  }, [formConfig, initialValues, registerForm, unregisterForm]);
  
  // Listen for collaborative changes
  useEffect(() => {
    if (isCollaborative && formConfig?.formId) {
      const handleRemoteChanges = (changes) => {
        if (changes.formId === formConfig.formId) {
          setFormValues(prev => ({
            ...prev,
            [changes.fieldId]: changes.value
          }));
        }
      };
      
      receiveChanges(handleRemoteChanges);
    }
  }, [isCollaborative, formConfig, receiveChanges]);
  
  // Validate form logic
  const validateForm = () => {
    const newErrors = {};
    let isValid = true;
    
    formConfig.fields.forEach(field => {
      // Skip fields that are hidden due to dependencies
      if (isFieldHidden(field)) {
        return;
      }
      
      // Check required fields
      if (field.required && !formValues[field.id]) {
        newErrors[field.id] = `${field.label} is required`;
        isValid = false;
      }
      
      // Check validation rules
      if (field.validation && formValues[field.id]) {
        if (field.validation.pattern && !new RegExp(field.validation.pattern).test(formValues[field.id])) {
          newErrors[field.id] = field.validation.message || `Invalid format for ${field.label}`;
          isValid = false;
        }
        
        if (field.validation.min !== undefined && Number(formValues[field.id]) < field.validation.min) {
          newErrors[field.id] = field.validation.message || `${field.label} must be at least ${field.validation.min}`;
          isValid = false;
        }
        
        if (field.validation.max !== undefined && Number(formValues[field.id]) > field.validation.max) {
          newErrors[field.id] = field.validation.message || `${field.label} must not exceed ${field.validation.max}`;
          isValid = false;
        }
      }
    });
    
    setErrors(newErrors);
    return isValid;
  };
  
  // Check if a field should be hidden based on dependencies
  const isFieldHidden = (field) => {
    if (!field.dependsOn) return false;
    
    const { dependsOn } = field;
    const dependentFieldValue = formValues[dependsOn.field];
    
    // If the dependent field matches the condition, show or hide based on showWhen
    if (dependentFieldValue === dependsOn.value) {
      return !dependsOn.showWhen;
    }
    
    // If it doesn't match, do the opposite
    return dependsOn.showWhen;
  };
  
  // Handle field changes
  const handleFieldChange = (fieldId, value) => {
    // Update form values
    setFormValues(prev => ({
      ...prev,
      [fieldId]: value
    }));
    
    // Clear error for this field
    if (errors[fieldId]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[fieldId];
        return newErrors;
      });
    }
    
    setIsDirty(true);
    
    // Share changes for collaboration
    if (isCollaborative) {
      shareChanges({
        formId: formConfig.formId,
        fieldId,
        value
      });
    }
    
    // Calculate dependent computed fields
    updateComputedFields(fieldId);
  };
  
  // Update computed fields when dependencies change
  const updateComputedFields = (changedFieldId) => {
    // Find computed fields that might depend on the changed field
    const computedFields = formConfig.fields.filter(field => field.computed);
    
    if (computedFields.length === 0) return;
    
    // Simple approach - update all computed fields
    // In a real implementation, we'd use a dependency graph to determine which fields to update
    const computedValues = {};
    
    computedFields.forEach(field => {
      if (field.formula && formConfig.calculations[field.formula]) {
        try {
          // Create a function from the formula string with all current field values as variables
          const formulaFn = new Function(...Object.keys(formValues), formConfig.calculations[field.formula]);
          const result = formulaFn(...Object.values(formValues));
          computedValues[field.id] = result;
        } catch (error) {
          console.error(`Error calculating ${field.id}:`, error);
        }
      }
    });
    
    if (Object.keys(computedValues).length > 0) {
      setFormValues(prev => ({
        ...prev,
        ...computedValues
      }));
    }
  };
  
  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (validateForm()) {
      onSubmit(formValues);
      setIsDirty(false);
    }
  };
  
  // Apply a template to the form
  const applyTemplate = (templateId) => {
    const template = formConfig.templates.find(t => t.id === templateId);
    if (template) {
      setFormValues(prev => ({
        ...prev,
        ...template.fieldValues
      }));
      setIsDirty(true);
    }
  };
  
  // Render the form based on configuration
  return (
    <form onSubmit={handleSubmit} className="dynamic-form">
      <div className="form-header">
        <h2>{formConfig.formName}</h2>
        
        {/* Template selector */}
        {formConfig.templates && formConfig.templates.length > 0 && (
          <div className="template-selector">
            <label>Apply Template:</label>
            <select 
              onChange={(e) => applyTemplate(e.target.value)}
              defaultValue=""
            >
              <option value="" disabled>Select a template</option>
              {formConfig.templates.map(template => (
                <option key={template.id} value={template.id}>
                  {template.name}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>
      
      {/* Tabbed layout */}
      {formConfig.layout.type === 'tabbed' && (
        <>
          <div className="form-tabs">
            {formConfig.layout.tabs.map(tab => (
              <button
                key={tab.id}
                type="button"
                className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
                onClick={() => setActiveTab(tab.id)}
              >
                {tab.label}
              </button>
            ))}
          </div>
          
          <div className="tab-content">
            {formConfig.layout.tabs.map(tab => (
              <div 
                key={tab.id}
                className={`tab-pane ${activeTab === tab.id ? 'active' : 'hidden'}`}
              >
                {tab.sections.map(section => (
                  <FormSection
                    key={section.id}
                    section={section}
                    fields={formConfig.fields.filter(field => 
                      section.fields.includes(field.id)
                    )}
                    values={formValues}
                    errors={errors}
                    onChange={handleFieldChange}
                    isFieldHidden={isFieldHidden}
                    readOnly={readOnly}
                    usersEditingFields={usersEditingFields}
                  />
                ))}
              </div>
            ))}
          </div>
        </>
      )}
      
      {/* Accordion layout or simple layout would go here */}
      
      <FormControls 
        isDirty={isDirty}
        onReset={() => {
          setFormValues(initialValues);
          setErrors({});
          setIsDirty(false);
        }}
        readOnly={readOnly}
      />
    </form>
  );
};

export default DynamicForm;