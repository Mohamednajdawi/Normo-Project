# Metadata Sidebar Feature

The Normo frontend now includes a **Metadata Sidebar** that displays extracted information from your legal queries on the right side of the interface.

## What it Shows

The sidebar displays metadata extracted by the AI from your query, helping you understand how the system interprets your legal question:

### 🌍 **Location Information**
- **Country**: Austria (for Austrian legal documents)
- **State/Region**: Upper Austria (Oberösterreich) when relevant

### ⚖️ **Legal Classification**
- **Legal Domain**: The area of law (e.g., planning_law, building_law, environmental_law)
- **Document Type**: Type of legal document (e.g., Bauordnung, Gesetz, Verordnung)  
- **Subject Area**: Specific topic (e.g., spatial_planning, building_construction, waste_management)

### 🏗️ **Additional Fields**
Any other metadata extracted from your query will appear in the "Additional Fields" section.

## How it Works

1. **Ask a Question**: Type your legal query about Austrian building regulations
2. **AI Analysis**: The system analyzes your query and extracts relevant metadata
3. **Sidebar Appears**: The metadata sidebar automatically appears on the right side
4. **Visual Indicators**: 
   - ✅ **Green chips**: Successfully identified information
   - **Gray chips**: Information not specified or unknown

## Example Queries

### Building Planning Query
**Query**: "I am building apartment building with 5 flats in Linz. How many square meters of playground do I have to plan?"

**Expected Metadata**:
- **Country**: Austria
- **State**: Upper Austria  
- **Legal Domain**: planning_law
- **Document Type**: Bauordnung
- **Subject Area**: spatial_planning

### Waste Management Query
**Query**: "What waste management regulations apply in Upper Austria?"

**Expected Metadata**:
- **Country**: Austria
- **State**: Upper Austria
- **Legal Domain**: environmental_law
- **Document Type**: Gesetz
- **Subject Area**: waste_management

## Visual Design

### 🎨 **ChatGPT-Style Interface**
- **Right sidebar**: Appears automatically when metadata is available
- **Dark theme**: Matches the main chat interface
- **Color coding**: Green for Austrian context, clear visual hierarchy
- **Responsive**: Adjusts to different screen sizes

### 📱 **Layout**
```
[Sidebar] | [Main Chat Area] | [Metadata Sidebar]
```

### 🔍 **Metadata Categories**
Each metadata field is displayed with:
- **Icon**: Visual representation of the field type
- **Label**: Human-readable field name  
- **Chip**: Colored indicator showing the value
- **Status**: Visual indication if information was extracted

## Benefits

### 🎯 **For Users**
- **Transparency**: See how AI interprets your legal question
- **Context**: Understand which legal domain applies
- **Accuracy**: Verify the system is analyzing the correct jurisdiction

### 🎯 **For Legal Professionals**
- **Classification**: Clear categorization of legal queries
- **Jurisdiction**: Confirm correct state and legal domain
- **Document Types**: Understand which legal instruments apply

### 🎯 **For System Understanding**
- **Debug**: See if AI correctly identifies query context
- **Optimization**: Understand how different queries are classified
- **Training**: Improve query analysis based on metadata extraction

## Technical Details

### 🔧 **Implementation**
- **Component**: `MetadataSidebar.tsx`
- **Integration**: Embedded in `ChatInterface.tsx`
- **Data Flow**: Metadata from API → ChatInterface → MetadataSidebar
- **State Management**: Tracks current metadata for latest query

### 📊 **Data Structure**
```typescript
interface Metadata {
  country?: string;
  state?: string;
  legal_domain?: string;
  document_type?: string;
  subject_area?: string;
  [key: string]: string; // Additional custom fields
}
```

### ⚙️ **Behavior**
- **Auto-hide**: Sidebar only appears when metadata is available
- **Persistence**: Shows metadata from the most recent query
- **Reset**: Clears when starting a new chat
- **Fallback**: Gracefully handles missing or incomplete metadata

## Future Enhancements

### 🚀 **Potential Features**
- **Confidence Scores**: Show how confident AI is about metadata extraction
- **Interactive Filters**: Click metadata to filter document results
- **Historical View**: See metadata from previous queries in the chat
- **Export Options**: Save metadata for legal documentation
- **Custom Fields**: Allow users to add custom metadata categories

### 🔄 **Improvements**
- **Smart Suggestions**: Suggest related legal queries based on metadata
- **Document Preview**: Show relevant legal documents for each metadata field
- **Jurisdiction Switching**: Quick toggle between Austrian states
- **Language Support**: Multi-language metadata display

The metadata sidebar enhances the legal research experience by providing transparent, categorized information about how your queries are being analyzed and processed.
