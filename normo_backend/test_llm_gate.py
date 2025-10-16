#!/usr/bin/env python3
"""
Test script for LLM Gate functionality.
This script tests the gate's ability to distinguish between architectural and general queries.
"""

import os
import sys
import requests
import json

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from normo_backend.agents.llm_gate import llm_gate

def test_gate_decisions():
    """Test the LLM gate's decision making."""
    print("🧪 Testing LLM Gate Decisions")
    print("=" * 50)
    
    # Test cases: (query, expected_use_agent, description)
    test_cases = [
        # General queries - should NOT use agent
        ("Hello", False, "General greeting"),
        ("How are you?", False, "General greeting"),
        ("What can you do?", False, "System information"),
        ("Help", False, "General help request"),
        ("Thank you", False, "General politeness"),
        ("Goodbye", False, "General farewell"),
        ("What is your name?", False, "General question"),
        ("Summarize our conversation", False, "General conversation summary"),
        
        # Architectural queries - should use agent
        ("What are the building requirements in Austria?", True, "Building requirements"),
        ("I need to know about playground area requirements", True, "Architectural calculation"),
        ("What are the fire safety regulations?", True, "Fire safety regulations"),
        ("How do I calculate the minimum room height?", True, "Architectural calculation"),
        ("What are the OIB guidelines for accessibility?", True, "OIB guidelines"),
        ("I'm building a 5-flat apartment building in Linz", True, "Building project"),
        ("What are the energy efficiency standards?", True, "Energy standards"),
        ("Can you help me with building codes?", True, "Building codes"),
        ("What are the minimum dimensions for stairs?", True, "Stair dimensions"),
        ("I need information about Austrian construction law", True, "Construction law"),
    ]
    
    correct_predictions = 0
    total_tests = len(test_cases)
    
    for query, expected_use_agent, description in test_cases:
        print(f"\n🔍 Testing: '{query}'")
        print(f"   Description: {description}")
        print(f"   Expected: {'Agent' if expected_use_agent else 'Simple LLM'}")
        
        try:
            decision = llm_gate.should_use_agent(query)
            actual_use_agent = decision["use_agent"]
            reason = decision["reason"]
            
            print(f"   Actual: {'Agent' if actual_use_agent else 'Simple LLM'}")
            print(f"   Reason: {reason}")
            
            if actual_use_agent == expected_use_agent:
                print("   ✅ CORRECT")
                correct_predictions += 1
            else:
                print("   ❌ INCORRECT")
                
        except Exception as e:
            print(f"   💥 ERROR: {e}")
    
    accuracy = (correct_predictions / total_tests) * 100
    print(f"\n📊 Gate Decision Accuracy: {correct_predictions}/{total_tests} ({accuracy:.1f}%)")
    
    return accuracy >= 80  # Consider 80%+ accuracy as good

def test_simple_responses():
    """Test simple LLM responses for general queries."""
    print("\n💬 Testing Simple LLM Responses")
    print("=" * 50)
    
    general_queries = [
        "Hello, how are you?",
        "What can you help me with?",
        "Thank you for your help",
        "Can you explain what you do?",
    ]
    
    for query in general_queries:
        print(f"\n🔍 Testing: '{query}'")
        try:
            response = llm_gate.get_simple_response(query)
            print(f"   Response: {response[:100]}...")
            print("   ✅ Response generated successfully")
        except Exception as e:
            print(f"   💥 ERROR: {e}")

def test_api_integration():
    """Test the API integration with LLM gate."""
    print("\n🌐 Testing API Integration")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test general query (should use simple LLM)
    print("\n1. Testing general query...")
    try:
        response = requests.post(f"{base_url}/chat", json={
            "messages": [{"role": "user", "content": "Hello, how are you?"}]
        })
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Response: {data['message']['content'][:100]}...")
            print(f"   Source citations: {len(data.get('source_citations', []))}")
        else:
            print(f"   ❌ API error: {response.status_code}")
    except Exception as e:
        print(f"   💥 Connection error: {e}")
        return False
    
    # Test architectural query (should use agent)
    print("\n2. Testing architectural query...")
    try:
        response = requests.post(f"{base_url}/chat", json={
            "messages": [{"role": "user", "content": "What are the building height requirements in Austria?"}]
        })
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Response: {data['message']['content'][:100]}...")
            print(f"   Source citations: {len(data.get('source_citations', []))}")
        else:
            print(f"   ❌ API error: {response.status_code}")
    except Exception as e:
        print(f"   💥 Connection error: {e}")
        return False
    
    return True

def main():
    """Main test function."""
    print("🚀 LLM Gate Test Suite")
    print("=" * 60)
    
    # Test gate decisions
    gate_success = test_gate_decisions()
    
    # Test simple responses
    test_simple_responses()
    
    # Test API integration
    api_success = test_api_integration()
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 30)
    print(f"Gate Decisions: {'✅ PASS' if gate_success else '❌ FAIL'}")
    print(f"API Integration: {'✅ PASS' if api_success else '❌ FAIL'}")
    
    if gate_success and api_success:
        print("\n🎉 All tests passed! LLM Gate is working correctly.")
        return 0
    else:
        print("\n💥 Some tests failed. Please check the logs above.")
        return 1

if __name__ == "__main__":
    exit(main())
