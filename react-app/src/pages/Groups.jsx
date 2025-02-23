import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const Groups = () => {
  const [groups, setGroups] = useState([]);
  const [pendingInvitations, setPendingInvitations] = useState([]);
  const [newGroupName, setNewGroupName] = useState('');
  const [inviteUsername, setInviteUsername] = useState('');
  const [selectedGroupId, setSelectedGroupId] = useState(null);
  const [selectedGroupMembers, setSelectedGroupMembers] = useState(null);
  const [selectedGroupName, setSelectedGroupName] = useState(null);
  const [selectedGroupVirtualCard, setSelectedGroupVirtualCard] = useState(null);
  const [selectedGroupSubscriptions, setSelectedGroupSubscriptions] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [memberRatios, setMemberRatios] = useState({});
  const [isEditingRatios, setIsEditingRatios] = useState(false);
  const navigate = useNavigate();

  const fetchGroupRatios = async (groupId) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8000/groups/${groupId}/ratios`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (!response.ok) throw new Error('Failed to fetch group ratios');
      const data = await response.json();
      const ratioMap = {};
      data.ratios.forEach(ratio => {
        ratioMap[ratio.user_id] = ratio.ratio_percentage;
      });
      setMemberRatios(ratioMap);
    } catch (err) {
      setError('Failed to load group ratios');
    }
  };

  const updateGroupRatios = async (groupId) => {
    try {
      const token = localStorage.getItem('access_token');
      const ratios = Object.entries(memberRatios).map(([user_id, ratio_percentage]) => ({
        user_id: parseInt(user_id),
        ratio_percentage: parseFloat(ratio_percentage)
      }));

      const response = await fetch(`http://localhost:8000/groups/${groupId}/ratios`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ ratios }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to update ratios');
      }

      setSuccess('Payment ratios updated successfully!');
      setIsEditingRatios(false);
    } catch (err) {
      setError(err.message || 'Failed to update ratios');
    }
  };

  const fetchGroups = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/groups/my', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (!response.ok) throw new Error('Failed to fetch groups');
      const data = await response.json();
      setGroups(data);
    } catch (err) {
      setError('Failed to load groups');
    }
  };

  const fetchPendingInvitations = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/groups/invitations/pending', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (!response.ok) throw new Error('Failed to fetch invitations');
      const data = await response.json();
      setPendingInvitations(data);
    } catch (err) {
      setError('Failed to load invitations');
    }
  };

  const fetchGroupSubscriptions = async (groupId) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8000/groups/${groupId}/subscriptions`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (!response.ok) throw new Error('Failed to fetch group subscriptions');
      const data = await response.json();
      setSelectedGroupSubscriptions(data);
    } catch (err) {
      setError('Failed to load group subscriptions');
    }
  };

  const handleGroupClick = async (groupId, groupName) => {
    setSelectedGroupId(groupId);
    setSelectedGroupName(groupName);
    setIsEditingRatios(false);
    setError(''); // Clear any previous errors
    
    try {
      const token = localStorage.getItem('access_token');
      
      // Fetch group details including virtual card
      const groupResponse = await fetch(`http://localhost:8000/groups/${groupId}/card`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      
      if (!groupResponse.ok) {
        throw new Error('Failed to fetch group details');
      }
      
      const groupData = await groupResponse.json();
      setSelectedGroupVirtualCard(groupData);
      
      // Fetch group members
      const membersResponse = await fetch(`http://localhost:8000/groups/${groupId}/members`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      
      if (!membersResponse.ok) {
        throw new Error('Failed to fetch group members');
      }
      
      const membersData = await membersResponse.json();
      setSelectedGroupMembers(membersData);
      
      // Fetch group ratios
      await fetchGroupRatios(groupId);

      // Fetch group subscriptions
      await fetchGroupSubscriptions(groupId);
      
    } catch (err) {
      console.error('Error fetching group details:', err);
      setError('Failed to load group details');
    }
  };

  useEffect(() => {
    fetchGroups();
    fetchPendingInvitations();
  }, []);

  const createGroup = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/groups/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ name: newGroupName }),
      });
      if (!response.ok) throw new Error('Failed to create group');
      setSuccess('Group created successfully!');
      setNewGroupName('');
      fetchGroups();
    } catch (err) {
      setError('Failed to create group');
    }
  };

  const inviteUser = async (e) => {
    e.preventDefault();
    if (!selectedGroupId) {
      setError('Please select a group first');
      return;
    }
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8000/groups/${selectedGroupId}/invite`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ username: inviteUsername }),
      });
      if (!response.ok) throw new Error('Failed to invite user');
      setSuccess('Invitation sent successfully!');
      setInviteUsername('');
    } catch (err) {
      setError('Failed to invite user');
    }
  };

  const acceptInvitation = async (invitationId) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8000/groups/invitations/${invitationId}/accept`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (!response.ok) throw new Error('Failed to accept invitation');
      setSuccess('Successfully joined the group!');
      fetchGroups();
      fetchPendingInvitations();
    } catch (err) {
      setError('Failed to accept invitation');
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8 text-center bg-gradient-to-r from-purple-400 to-pink-600 bg-clip-text text-transparent">
          Groups
        </h1>

        {error && (
          <div className="bg-red-500 text-white p-3 rounded mb-4">
            {error}
          </div>
        )}
        {success && (
          <div className="bg-green-500 text-white p-3 rounded mb-4">
            {success}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Create Group Form */}
          <div className="bg-gray-800 p-6 rounded-lg">
            <h2 className="text-xl font-semibold mb-4">Create New Group</h2>
            <form onSubmit={createGroup} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Group Name
                </label>
                <input
                  type="text"
                  value={newGroupName}
                  onChange={(e) => setNewGroupName(e.target.value)}
                  className="w-full p-2 rounded bg-gray-700 text-white"
                  required
                />
              </div>
              <button
                type="submit"
                className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded"
              >
                Create Group
              </button>
            </form>
          </div>

          {/* Invite User Form */}
          <div className="bg-gray-800 p-6 rounded-lg">
            <h2 className="text-xl font-semibold mb-4">Invite User</h2>
            <form onSubmit={inviteUser} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Select Group
                </label>
                <select
                  value={selectedGroupId || ''}
                  onChange={(e) => setSelectedGroupId(e.target.value)}
                  className="w-full p-2 rounded bg-gray-700 text-white"
                  required
                >
                  <option value="">Select a group</option>
                  {groups
                    .filter((group) => group.is_admin)
                    .map((group) => (
                      <option key={group.id} value={group.id}>
                        {group.group_name}
                      </option>
                    ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">
                  Username
                </label>
                <input
                  type="text"
                  value={inviteUsername}
                  onChange={(e) => setInviteUsername(e.target.value)}
                  className="w-full p-2 rounded bg-gray-700 text-white"
                  required
                />
              </div>
              <button
                type="submit"
                className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded"
              >
                Send Invitation
              </button>
            </form>
          </div>
        </div>

        {/* My Groups */}
        <div className="mt-8 bg-gray-800 p-6 rounded-lg">
          <h2 className="text-xl font-semibold mb-4">My Groups</h2>
          {groups.length === 0 ? (
            <p className="text-gray-400">You're not a member of any groups yet.</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {groups.map((group) => (
                <div
                  key={group.id}
                  className="bg-gray-700 p-4 rounded-lg cursor-pointer hover:bg-gray-600 transition-colors"
                  onClick={() => handleGroupClick(group.id, group.group_name)}
                >
                  <h3 className="font-semibold">{group.group_name}</h3>
                  <p className="text-sm text-gray-400">
                    {group.is_admin ? 'Admin' : 'Member'}
                  </p>
                </div>
              ))}
            </div>
          )}

          {/* Selected Group Details */}
          {selectedGroupId && (
            <div className="mt-6 bg-gray-700 p-6 rounded-lg">
              <h3 className="text-2xl font-semibold mb-4">{selectedGroupName}</h3>
              
              {/* Card Details */}
              {selectedGroupVirtualCard && selectedGroupVirtualCard.card_details && (
                <div className="mb-6 bg-gray-800 p-4 rounded-lg">
                  <h4 className="text-lg font-semibold mb-3 text-purple-400">Virtual Card Details</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-gray-400">Card Number</p>
                      <p className="font-medium">{selectedGroupVirtualCard.card_details.number}</p>
                    </div>
                    <div>
                      <p className="text-gray-400">Virtual Card ID</p>
                      <p className="font-medium">{selectedGroupVirtualCard.virtual_card_id}</p>
                    </div>
                    <div>
                      <p className="text-gray-400">Expiry</p>
                      <p className="font-medium">{selectedGroupVirtualCard.card_details.exp_month}/{selectedGroupVirtualCard.card_details.exp_year}</p>
                    </div>
                    <div>
                      <p className="text-gray-400">CVV</p>
                      <p className="font-medium">{selectedGroupVirtualCard.card_details.cvc}</p>
                    </div>
                    <div>
                      <p className="text-gray-400">Status</p>
                      <p className="font-medium capitalize">{selectedGroupVirtualCard.card_details.status}</p>
                    </div>
                    <div>
                      <p className="text-gray-400">Type</p>
                      <p className="font-medium capitalize">{selectedGroupVirtualCard.card_details.type}</p>
                    </div>
                  </div>
                </div>
              )}
              
              {/* Group Subscriptions */}
              {selectedGroupSubscriptions && (
                <div className="mb-6 bg-gray-800 p-4 rounded-lg">
                  <h4 className="text-lg font-semibold mb-3 text-purple-400">Group Subscriptions</h4>
                  {selectedGroupSubscriptions.length === 0 ? (
                    <p className="text-gray-400">No subscriptions in this group yet.</p>
                  ) : (
                    <div className="space-y-3">
                      {selectedGroupSubscriptions.map((subscription) => (
                        <div key={subscription.id} className="bg-gray-700 p-3 rounded flex justify-between items-center">
                          <div>
                            <p className="font-medium">{subscription.description}</p>
                            <p className="text-sm text-gray-400">
                              Next payment: {new Date(subscription.estimated_next_date).toLocaleDateString()}
                            </p>
                          </div>
                          <div className="text-right">
                            <p className="font-bold text-green-400">€{subscription.amount.toFixed(2)}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
              
              {/* Members and Ratios */}
              {selectedGroupMembers && (
                <div>
                  <div className="flex justify-between items-center mb-3">
                    <h4 className="text-lg font-semibold text-purple-400">Members & Ratios</h4>
                    {groups.find(g => g.id === selectedGroupId)?.is_admin && (
                      <div className="flex space-x-2">
                        {isEditingRatios ? (
                          <>
                            <button
                              onClick={() => updateGroupRatios(selectedGroupId)}
                              className="px-3 py-1 text-sm bg-green-600 hover:bg-green-700 rounded"
                            >
                              Save Ratios
                            </button>
                            <button
                              onClick={() => {
                                setIsEditingRatios(false);
                                fetchGroupRatios(selectedGroupId);
                              }}
                              className="px-3 py-1 text-sm bg-gray-600 hover:bg-gray-700 rounded"
                            >
                              Cancel
                            </button>
                          </>
                        ) : (
                          <button
                            onClick={() => setIsEditingRatios(true)}
                            className="px-3 py-1 text-sm bg-purple-600 hover:bg-purple-700 rounded"
                          >
                            Edit Ratios
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                  <div className="space-y-3">
                    {selectedGroupMembers.map((member) => (
                      <div key={member.id} className="p-4 rounded bg-gray-800">
                        <div className="flex items-center justify-between mb-2">
                          <div>
                            <p className="font-medium">{member.username}</p>
                            <p className="text-sm text-gray-400">{member.first_name} {member.last_name}</p>
                          </div>
                          <div className="flex items-center space-x-2">
                            <span className="px-2 py-1 text-xs rounded bg-gray-600">
                              {member.is_admin ? 'Admin' : 'Member'}
                            </span>
                          </div>
                        </div>
                        <div className="flex items-center space-x-4">
                          {isEditingRatios ? (
                            <div className="flex-1 flex items-center space-x-4">
                              <input
                                type="range"
                                min="0"
                                max="100"
                                step="1"
                                value={memberRatios[member.id] || 0}
                                onChange={(e) => {
                                  const newRatios = { ...memberRatios };
                                  newRatios[member.id] = parseFloat(e.target.value);
                                  setMemberRatios(newRatios);
                                }}
                                className="flex-1 h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-purple-600"
                              />
                              <input
                                type="number"
                                min="0"
                                max="100"
                                step="1"
                                value={memberRatios[member.id] || 0}
                                onChange={(e) => {
                                  const newRatios = { ...memberRatios };
                                  newRatios[member.id] = parseFloat(e.target.value);
                                  setMemberRatios(newRatios);
                                }}
                                className="w-20 px-2 py-1 text-sm rounded bg-gray-700 text-white"
                              />
                              <span className="text-sm text-gray-400">%</span>
                            </div>
                          ) : (
                            <div className="flex-1 flex items-center space-x-4">
                              <div className="flex-1 h-2 bg-gray-700 rounded-lg overflow-hidden">
                                <div 
                                  className="h-full bg-purple-600" 
                                  style={{ width: `${memberRatios[member.id] || 0}%` }}
                                />
                              </div>
                              <span className="px-3 py-1 text-sm rounded bg-purple-600 min-w-[60px] text-center">
                                {memberRatios[member.id] || 0}%
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                  {isEditingRatios && (
                    <div className="mt-4 p-3 bg-gray-800 rounded">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-400">Total:</span>
                        <span className={`font-medium ${
                          Object.values(memberRatios).reduce((a, b) => a + parseFloat(b || 0), 0) === 100 
                          ? 'text-green-400' 
                          : 'text-red-400'
                        }`}>
                          {Object.values(memberRatios).reduce((a, b) => a + parseFloat(b || 0), 0)}%
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Pending Invitations */}
        <div className="mt-8 bg-gray-800 p-6 rounded-lg">
          <h2 className="text-xl font-semibold mb-4">Pending Invitations</h2>
          {pendingInvitations.length === 0 ? (
            <p className="text-gray-400">No pending invitations.</p>
          ) : (
            <div className="space-y-4">
              {pendingInvitations.map((invitation) => (
                <div
                  key={invitation.id}
                  className="bg-gray-700 p-4 rounded-lg flex items-center justify-between"
                >
                  <div>
                    <p>
                      <span className="font-semibold">{invitation.group_name}</span>
                    </p>
                    <p className="text-sm text-gray-400">
                      Invited by {invitation.inviter_username}
                    </p>
                  </div>
                  <button
                    onClick={() => acceptInvitation(invitation.id)}
                    className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
                  >
                    Accept
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Groups;
